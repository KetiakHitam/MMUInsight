from flask import render_template, redirect, url_for, flash, request
import re
from flask_login import current_user
from . import auth_bp
from auth.decorators import login_required, admin_required
from models import User, Report, Review, AuditLog
from extensions import db
from audit import log_admin_action

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    return "Student dashboard (placeholder - requires login)"

@auth_bp.route("/admin")
@admin_required
def admin_dashboard():
    users = User.query.all()
    total_users = len(users)
    verified_users = sum(1 for u in users if u.is_verified)
    admin_count = sum(1 for u in users if u.is_admin())
    student_count = sum(1 for u in users if u.user_type == 'student')
    lecturer_count = sum(1 for u in users if u.user_type == 'lecturer')
    unverified_lecturers = sum(1 for u in users if u.user_type == 'lecturer' and not u.is_claimed)
    total_reviews = Review.query.count()
    
    pending_reports = Report.query.filter_by(status='pending').count()
    flagged_reviews = Review.query.filter_by(requires_human_review=True, is_approved=None).count()

    return render_template(
        "admin_dashboard.html",
        users=users,             
        total_users=total_users,
        verified_users=verified_users,
        admin_count=admin_count,
        pending_reports=pending_reports,
        student_count=student_count,
        lecturer_count=lecturer_count,
        unverified_lecturers=unverified_lecturers,
        total_reviews=total_reviews,
        flagged_reviews=flagged_reviews,
    )

@auth_bp.route("/admin/users")
@admin_required
def admin_users():
    users = User.query.all()
    return render_template("admin_users.html", users=users)

@auth_bp.route("/admin/user/<int:user_id>/verify", methods=["POST"])
@admin_required
def admin_verify_user(user_id):
    user = User.query.get(user_id)
    if user and current_user and current_user.can_manage_user(user):
        user.is_verified = True
        db.session.commit()
        log_admin_action(f"Verified user {user.email}", "user")
    return redirect(url_for("auth.admin_users"))

@auth_bp.route("/admin/user/<int:user_id>/make-admin", methods=["POST"])
@admin_required
def admin_make_admin(user_id):
    user = User.query.get(user_id)
    if user and current_user.can_change_role(user, 'ADMIN'):
        user.role = 'ADMIN'
        db.session.commit()
        log_admin_action(f"Made user {user.email} ADMIN", "user")
        flash(f"{user.email} is now an ADMIN", "success")
    else:
        flash("You don't have permission to assign this role", "danger")
    return redirect(url_for("auth.admin_users"))

@auth_bp.route("/admin/user/<int:user_id>/make-mod", methods=["POST"])
@admin_required
def admin_make_mod(user_id):
    user = User.query.get(user_id)
    if user and current_user.can_change_role(user, 'MOD'):
        user.role = 'MOD'
        db.session.commit()
        log_admin_action(f"Made user {user.email} MOD", "user")
        flash(f"{user.email} is now a MOD", "success")
    else:
        flash("You don't have permission to assign this role", "danger")
    return redirect(url_for("auth.admin_users"))

@auth_bp.route("/admin/user/<int:user_id>/remove-role", methods=["POST"])
@admin_required
def admin_remove_role(user_id):
    user = User.query.get(user_id)
    if user and current_user.can_manage_user(user) and not user.is_owner():
        user.role = None
        db.session.commit()
        log_admin_action(f"Removed role from user {user.email}", "user")
        flash(f"Role removed from {user.email}", "success")
    else:
        flash("You don't have permission to remove this role", "danger")
    return redirect(url_for("auth.admin_users"))

@auth_bp.route("/admin/user/<int:user_id>/suspend", methods=["POST"])
@admin_required
def admin_suspend_user(user_id):
    user = User.query.get(user_id)
    if user and current_user.can_suspend_user(user):
        user.is_verified = False    
        db.session.commit()
        log_admin_action(f"Suspended user {user.email}", "user")
        flash(f"{user.email} has been suspended", "success")
    else:
        flash("You don't have permission to suspend this user", "danger")
    return redirect(url_for("auth.admin_users"))

@auth_bp.route("/admin/user/<int:user_id>/delete", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get(user_id)
    if user and current_user.can_delete_user(user):
        deleted_user_email = user.email
        db.session.delete(user)
        db.session.commit()
        log_admin_action(f"Deleted user {deleted_user_email}", "user")
        flash(f"{deleted_user_email} has been deleted", "success")
    else:
        flash("You don't have permission to delete this user", "danger")
    return redirect(url_for("auth.admin_users"))

@auth_bp.route("/admin/reports")
@admin_required
def admin_reports():
    reports = Report.query.order_by(Report.report_date.desc()).all()
    return render_template("admin_reports.html", reports=reports)

@auth_bp.route("/admin/report/<int:report_id>/dismiss")
@admin_required
def admin_dismiss_report(report_id):
    report = Report.query.get(report_id)
    if report:
        report.status = 'dismissed'
        db.session.commit()
        log_admin_action(f"Dismissed report {report.id}", "review")
        flash("Report dismissed", "success")
    return redirect(url_for("auth.admin_reports"))

@auth_bp.route("/admin/report/<int:report_id>/delete-review")
@admin_required
def admin_delete_reported_review(report_id):
    report = Report.query.get(report_id)
    if report:
        review = report.review
        review_id = review.id if review else None
        if review:
            db.session.delete(review)
        report.status = 'deleted'
        db.session.commit()
        log_admin_action(f"Deleted reported review {review_id} via report {report.id}", "review")
        flash("Review deleted", "success")
    return redirect(url_for("auth.admin_reports"))


@auth_bp.route("/admin/audit-logs")
@admin_required
def admin_audit_logs():
    # Ensure the table exists for older databases.
    try:
        AuditLog.__table__.create(db.engine, checkfirst=True)
    except Exception:
        pass

    email_q = (request.args.get("email") or "").strip()
    action_q = (request.args.get("action") or "").strip()
    target_q = (request.args.get("target") or "").strip()

    query = AuditLog.query.outerjoin(User, AuditLog.user_id == User.id)

    if email_q:
        query = query.filter(User.email.ilike(f"%{email_q}%"))
    if action_q:
        query = query.filter(AuditLog.action.ilike(f"%{action_q}%"))
    if target_q:
        query = query.filter(AuditLog.target_type == target_q)

    logs = query.order_by(AuditLog.timestamp.desc()).limit(200).all()

    # Backwards-compatible display: older logs stored user IDs in the action string.
    # Convert those to emails when possible.
    user_id_matches: list[tuple[AuditLog, re.Match[str]]] = []
    target_user_ids: set[int] = set()
    user_action_patterns = [
        r"^(Verified user) (\d+)$",
        r"^(Suspended user) (\d+)$",
        r"^(Deleted user) (\d+)$",
        r"^(Removed role from user) (\d+)$",
        r"^(Made user) (\d+) (ADMIN|MOD)$",
    ]

    for log in logs:
        action_text = (log.action or "").strip()
        for pattern in user_action_patterns:
            m = re.match(pattern, action_text)
            if not m:
                continue

            if len(m.groups()) == 2:
                target_user_ids.add(int(m.group(2)))
            elif len(m.groups()) == 3:
                target_user_ids.add(int(m.group(2)))

            user_id_matches.append((log, m))
            break

    user_email_by_id: dict[int, str] = {}
    if target_user_ids:
        users = User.query.filter(User.id.in_(list(target_user_ids))).all()
        user_email_by_id = {u.id: u.email for u in users}

    for log, m in user_id_matches:
        if len(m.groups()) == 2:
            prefix = m.group(1)
            uid = int(m.group(2))
            email = user_email_by_id.get(uid)
            if email:
                log.display_action = f"{prefix} {email}"
        elif len(m.groups()) == 3:
            prefix = m.group(1)
            uid = int(m.group(2))
            role = m.group(3)
            email = user_email_by_id.get(uid)
            if email:
                log.display_action = f"{prefix} {email} {role}"

    return render_template(
        "admin_audit_logs.html",
        logs=logs,
        email_q=email_q,
        action_q=action_q,
        target_q=target_q,
    )

@auth_bp.route("/admin/moderation")
@admin_required
def admin_moderation():
    """Display flagged reviews pending moderation"""
    # Get flagged reviews that haven't been approved/rejected yet
    flagged_reviews = Review.query.filter_by(
        requires_human_review=True, 
        is_approved=None
    ).order_by(Review.review_date.desc()).all()
    
    return render_template(
        "admin_moderation.html",
        flagged_reviews=flagged_reviews,
        count=len(flagged_reviews)
    )

@auth_bp.route("/admin/moderation/<int:review_id>/approve", methods=["POST"])
@admin_required
def approve_flagged_review(review_id):
    """Approve a flagged review"""
    review = Review.query.get_or_404(review_id)
    review.is_approved = True
    db.session.commit()
    log_admin_action(f"Approved flagged review {review_id}", "review")
    flash("Review approved and will now be visible.", "success")
    return redirect(url_for("auth.admin_moderation"))

@auth_bp.route("/admin/moderation/<int:review_id>/reject", methods=["POST"])
@admin_required
def reject_flagged_review(review_id):
    """Reject a flagged review"""
    review = Review.query.get_or_404(review_id)
    review.is_approved = False
    db.session.commit()
    log_admin_action(f"Rejected flagged review {review_id}", "review")
    flash("Review rejected and will not be visible.", "error")
    return redirect(url_for("auth.admin_moderation"))