from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_babel import gettext as _
from extensions import db, limiter
from models import BugReport, BugComment
from audit import log_admin_action
from datetime import datetime
from sqlalchemy import desc

bugs_bp = Blueprint('bugs', __name__)

@bugs_bp.route('/report-bug', methods=['GET', 'POST'])
@login_required
@limiter.limit("5 per hour")
def report_bug():
    if request.method == 'GET':
        return render_template('report_bug.html')
    
    # POST request
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if not title or not description:
        flash(_("Please provide both title and description"), "error")
        return redirect(url_for('bugs.report_bug'))
    
    if len(title) < 5 or len(title) > 200:
        flash(_("Title must be between 5 and 200 characters"), "error")
        return redirect(url_for('bugs.report_bug'))
    
    if len(description) < 10 or len(description) > 5000:
        flash(_("Description must be between 10 and 5000 characters"), "error")
        return redirect(url_for('bugs.report_bug'))
    
    # Create bug report
    bug = BugReport(
        title=title,
        description=description,
        user_id=current_user.id
    )
    
    db.session.add(bug)
    db.session.commit()
    
    flash(_("Thank you for reporting this bug. Our team will review it soon."), "success")
    return redirect(url_for('index'))

@bugs_bp.route('/admin/bugs', methods=['GET'])
@login_required
def admin_bugs():
    if not current_user.is_mod():
        flash(_("Access denied"), "error")
        return redirect(url_for('index'))
    
    # Filters
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    sort_by = request.args.get('sort', 'reported_at')
    
    query = BugReport.query
    
    if status_filter and status_filter in ['new', 'in_progress', 'resolved', 'closed']:
        query = query.filter_by(status=status_filter)
    
    if priority_filter and priority_filter in ['low', 'normal', 'high', 'critical']:
        query = query.filter_by(priority=priority_filter)
    
    # Sorting
    if sort_by == 'reported_at':
        query = query.order_by(desc(BugReport.reported_at))
    elif sort_by == 'updated_at':
        query = query.order_by(desc(BugReport.updated_at))
    elif sort_by == 'priority':
        priority_order = {'critical': 4, 'high': 3, 'normal': 2, 'low': 1}
        # SQLAlchemy doesn't support direct priority ordering, so we'll sort in Python
        bugs = query.all()
        bugs.sort(key=lambda x: priority_order.get(x.priority, 0), reverse=True)
        return render_template('admin_bugs.html', 
                             bugs=bugs,
                             current_status=status_filter,
                             current_priority=priority_filter,
                             current_sort=sort_by)
    else:
        query = query.order_by(desc(BugReport.reported_at))
    
    bugs = query.all()
    
    return render_template('admin_bugs.html', 
                         bugs=bugs,
                         current_status=status_filter,
                         current_priority=priority_filter,
                         current_sort=sort_by)

@bugs_bp.route('/admin/bugs/<int:bug_id>', methods=['GET'])
@login_required
def view_bug(bug_id):
    if not current_user.is_mod():
        flash(_("Access denied"), "error")
        return redirect(url_for('index'))
    
    bug = BugReport.query.get_or_404(bug_id)
    
    return render_template('bug_detail.html', bug=bug)

@bugs_bp.route('/admin/bugs/<int:bug_id>/update', methods=['POST'])
@login_required
def update_bug(bug_id):
    if not current_user.is_mod():
        return jsonify({'error': 'Access denied'}), 403
    
    bug = BugReport.query.get_or_404(bug_id)
    
    status = request.form.get('status', '')
    priority = request.form.get('priority', '')
    internal_notes = request.form.get('internal_notes', '').strip()
    resolution_notes = request.form.get('resolution_notes', '').strip()
    
    # Validate inputs
    if status and status not in ['new', 'in_progress', 'resolved', 'closed']:
        return jsonify({'error': 'Invalid status'}), 400
    
    if priority and priority not in ['low', 'normal', 'high', 'critical']:
        return jsonify({'error': 'Invalid priority'}), 400
    
    # Update fields
    if status:
        bug.status = status
    if priority:
        bug.priority = priority
    if internal_notes:
        bug.internal_notes = internal_notes
    if resolution_notes and status == 'closed':
        bug.resolution_notes = resolution_notes
    
    bug.updated_at = datetime.utcnow()
    db.session.commit()
    
    log_admin_action(f"Updated bug report #{bug.id} to status={status}, priority={priority}", "bug_report")
    
    return jsonify({'success': True, 'message': 'Bug updated successfully'})

@bugs_bp.route('/admin/bugs/<int:bug_id>/comment', methods=['POST'])
@login_required
def add_bug_comment(bug_id):
    if not current_user.is_mod():
        return jsonify({'error': 'Access denied'}), 403
    
    bug = BugReport.query.get_or_404(bug_id)
    
    comment_text = request.form.get('comment_text', '').strip()
    
    if not comment_text:
        return jsonify({'error': 'Comment cannot be empty'}), 400
    
    if len(comment_text) > 5000:
        return jsonify({'error': 'Comment too long'}), 400
    
    comment = BugComment(
        bug_report_id=bug_id,
        user_id=current_user.id,
        comment_text=comment_text
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Comment added',
        'comment': {
            'id': comment.id,
            'user': current_user.email,
            'text': comment_text,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })
