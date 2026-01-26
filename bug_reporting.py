from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_babel import gettext as _
from extensions import db, limiter
from models import BugReport, BugComment, User
from audit import log_admin_action
from datetime import datetime
from sqlalchemy import func

bug_bp = Blueprint('bugs', __name__)

@bug_bp.route('/report-bug', methods=['GET', 'POST'])
@login_required
@limiter.limit("5 per hour")
def report_bug():
    if request.method == 'GET':
        return render_template('report_bug.html')
    
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    affected_feature = request.form.get('affected_feature', '').strip()
    
    if not title or not description:
        flash(_("Title and description are required"), "error")
        return redirect(url_for('bugs.report_bug'))
    
    if len(title) > 200:
        flash(_("Title must be 200 characters or less"), "error")
        return redirect(url_for('bugs.report_bug'))
    
    bug = BugReport(
        user_id=current_user.id,
        title=title,
        description=description,
        affected_feature=affected_feature if affected_feature else None,
        status='new'
    )
    
    db.session.add(bug)
    db.session.commit()
    
    flash(_("Thank you for reporting the bug! Our team will look into it."), "success")
    return redirect(url_for('index'))

@bug_bp.route('/admin/bugs', methods=['GET'])
@login_required
def view_bugs():
    if not current_user.is_mod():
        flash(_("Access denied"), "error")
        return redirect(url_for('index'))
    
    # Filters
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    sort_by = request.args.get('sort', 'reported_at')
    sort_order = request.args.get('order', 'desc')
    
    query = BugReport.query
    
    if status_filter and status_filter in ['new', 'in_progress', 'resolved', 'closed']:
        query = query.filter_by(status=status_filter)
    
    if priority_filter and priority_filter in ['low', 'normal', 'high', 'critical']:
        query = query.filter_by(priority=priority_filter)
    
    # Sorting
    if sort_by == 'reported_at':
        query = query.order_by(BugReport.reported_at.desc() if sort_order == 'desc' else BugReport.reported_at.asc())
    elif sort_by == 'priority':
        # Custom sort: critical > high > normal > low > None
        priority_order = {'critical': 1, 'high': 2, 'normal': 3, 'low': 4}
        query = query.order_by(
            func.case(
                {v: k for k, v in priority_order.items()},
                value=BugReport.priority,
                else_=5
            ).desc() if sort_order == 'desc' else func.case(
                {v: k for k, v in priority_order.items()},
                value=BugReport.priority,
                else_=5
            ).asc()
        )
    elif sort_by == 'status':
        status_order = {'new': 1, 'in_progress': 2, 'resolved': 3, 'closed': 4}
        query = query.order_by(
            func.case(
                {v: k for k, v in status_order.items()},
                value=BugReport.status,
                else_=5
            ).desc() if sort_order == 'desc' else func.case(
                {v: k for k, v in status_order.items()},
                value=BugReport.status,
                else_=5
            ).asc()
        )
    
    bugs = query.all()
    
    return render_template('admin_bugs.html', 
                          bugs=bugs,
                          current_status=status_filter,
                          current_priority=priority_filter,
                          current_sort=sort_by,
                          current_order=sort_order)

@bug_bp.route('/admin/bug/<int:bug_id>', methods=['GET', 'POST'])
@login_required
def view_bug_detail(bug_id):
    if not current_user.is_mod():
        flash(_("Access denied"), "error")
        return redirect(url_for('index'))
    
    bug = BugReport.query.get_or_404(bug_id)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_status':
            new_status = request.form.get('status')
            if new_status in ['new', 'in_progress', 'resolved', 'closed']:
                bug.status = new_status
                if new_status == 'resolved':
                    bug.resolved_at = datetime.utcnow()
                    bug.resolved_by_id = current_user.id
                db.session.commit()
                log_admin_action(f"Updated bug #{bug.id} status to {new_status}", "bug")
                flash(_("Status updated"), "success")
        
        elif action == 'update_priority':
            new_priority = request.form.get('priority')
            if new_priority in ['low', 'normal', 'high', 'critical']:
                bug.priority = new_priority
                db.session.commit()
                log_admin_action(f"Updated bug #{bug.id} priority to {new_priority}", "bug")
                flash(_("Priority updated"), "success")
        
        elif action == 'add_resolution_notes':
            notes = request.form.get('resolution_notes', '').strip()
            if notes:
                bug.resolution_notes = notes
                db.session.commit()
                log_admin_action(f"Added resolution notes to bug #{bug.id}", "bug")
                flash(_("Resolution notes added"), "success")
        
        elif action == 'add_comment':
            comment_text = request.form.get('comment_text', '').strip()
            if comment_text:
                comment = BugComment(
                    bug_id=bug.id,
                    admin_id=current_user.id,
                    comment_text=comment_text
                )
                db.session.add(comment)
                db.session.commit()
                log_admin_action(f"Added comment to bug #{bug.id}", "bug")
                flash(_("Comment added"), "success")
        
        return redirect(url_for('bugs.view_bug_detail', bug_id=bug.id))
    
    return render_template('bug_detail.html', bug=bug)
