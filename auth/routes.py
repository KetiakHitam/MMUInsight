from flask import render_template, redirect, url_for, flash, request
import re
import uuid
from flask_login import current_user
from . import auth_bp
from auth.decorators import login_required, admin_required
from models import User, Report, Review, AuditLog
from extensions import db, bcrypt
from audit import log_admin_action
from datetime import datetime, timedelta

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    return "Student dashboard (placeholder - requires login)"

@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "GET":
        return render_template("change_password.html")
    
    current_password = request.form.get("current_password", "").strip()
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()
    
    # Validate current password
    if not bcrypt.check_password_hash(current_user.password_hash, current_password):
        flash("Current password is incorrect", "error")
        return render_template("change_password.html")
    
    # Validate new password matches confirm
    if new_password != confirm_password:
        flash("New passwords do not match", "error")
        return render_template("change_password.html")
    
    # Validate password meets requirements
    if len(new_password) < 8:
        flash("Password must be at least 8 characters", "error")
        return render_template("change_password.html")
    
    if not any(c.isupper() for c in new_password):
        flash("Password must contain at least one uppercase letter", "error")
        return render_template("change_password.html")
    
    if not any(c.islower() for c in new_password):
        flash("Password must contain at least one lowercase letter", "error")
        return render_template("change_password.html")
    
    if not any(c.isdigit() for c in new_password):
        flash("Password must contain at least one number", "error")
        return render_template("change_password.html")
    
    if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in new_password):
        flash("Password must contain at least one special character", "error")
        return render_template("change_password.html")
    
    # Update password
    current_user.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
    current_user.password_is_temporary = False
    db.session.commit()
    
    flash("Password changed successfully!", "success")
    return redirect(url_for("index"))

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
    flagged_reviews = Review.query.filter_by(requires_human_review=True).filter(
        db.or_(Review.is_approved == None, Review.is_approved == False)
    ).count()

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

@auth_bp.route("/admin/user/<int:user_id>/reset-password", methods=["POST"])
@admin_required
def admin_reset_password(user_id):
    user = User.query.get(user_id)
    if user and current_user.can_manage_user(user):
        # Generate temporary password
        temp_password = str(uuid.uuid4())[:12]
        user.password_hash = bcrypt.generate_password_hash(temp_password).decode("utf-8")
        user.password_is_temporary = True
        user.reset_token_created_at = datetime.utcnow()
        db.session.commit()
        log_admin_action(f"Reset password for user {user.email}", "user")
        flash(f"Password reset for {user.email}. Temporary password: {temp_password} (Expires in 24 hours - Share via secure email)", "success")
    else:
        flash("You don't have permission to reset this user's password", "danger")
    return redirect(url_for("auth.admin_users"))

@auth_bp.route("/admin/report/<int:report_id>/dismiss")
@admin_required
def admin_dismiss_report(report_id):
    from datetime import datetime
    report = Report.query.get(report_id)
    if report:
        report.status = 'dismissed'
        # Track moderation on the review
        if report.review:
            report.review.moderated_by_id = current_user.id
            report.review.moderated_at = datetime.utcnow()
            report.review.moderation_action = 'report_dismissed'
        db.session.commit()
        log_admin_action(f"Dismissed report {report.id}", "review")
        flash("Report dismissed", "success")
    return redirect(url_for("auth.admin_moderation", filter='reported'))

@auth_bp.route("/admin/report/<int:report_id>/delete-review")
@admin_required
def admin_delete_reported_review(report_id):
    from datetime import datetime
    report = Report.query.get(report_id)
    if report:
        review = report.review
        review_id = review.id if review else None
        if review:
            # Track moderation before deletion
            review.moderated_by_id = current_user.id
            review.moderated_at = datetime.utcnow()
            review.moderation_action = 'deleted_from_report'
            db.session.flush()  # Save moderation info before delete
            db.session.delete(review)
        report.status = 'deleted'
        db.session.commit()
        log_admin_action(f"Deleted reported review {review_id} via report {report.id}", "review")
        flash("Review deleted", "success")
    return redirect(url_for("auth.admin_moderation", filter='reported'))


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
    """Display flagged reviews and reported reviews pending moderation"""
    filter_type = request.args.get('filter', 'all')  # 'all', 'automod', 'reported'
    
    # Get auto-moderation flagged reviews (both is_approved=None and is_approved=False)
    flagged_reviews = Review.query.filter_by(requires_human_review=True).filter(
        db.or_(Review.is_approved == None, Review.is_approved == False)
    ).order_by(Review.review_date.desc()).all()
    
    # Get reported reviews (pending reports)
    reported_reviews_data = []
    pending_reports = Report.query.filter_by(status='pending').order_by(Report.report_date.desc()).all()
    
    # Group reports by review to avoid duplicates
    seen_review_ids = set()
    for report in pending_reports:
        if report.review_id not in seen_review_ids:
            seen_review_ids.add(report.review_id)
            # Get all reports for this review
            all_reports = Report.query.filter_by(review_id=report.review_id, status='pending').order_by(Report.report_date.desc()).all()
            reported_reviews_data.append({
                'review': report.review,
                'report_count': len(all_reports),
                'latest_report': report,
                'all_reports': all_reports
            })
    
    # Apply filter
    if filter_type == 'automod':
        reported_reviews_data = []
    elif filter_type == 'reported':
        flagged_reviews = []
    
    total_count = len(flagged_reviews) + len(reported_reviews_data)
    
    return render_template(
        "admin_moderation.html",
        flagged_reviews=flagged_reviews,
        reported_reviews=reported_reviews_data,
        count=total_count,
        filter_type=filter_type
    )

@auth_bp.route("/admin/moderation/<int:review_id>/approve", methods=["POST"])
@admin_required
def approve_flagged_review(review_id):
    """Approve a flagged review"""
    from datetime import datetime
    review = Review.query.get_or_404(review_id)
    review.is_approved = True
    review.moderated_by_id = current_user.id
    review.moderated_at = datetime.utcnow()
    review.moderation_action = 'approved'
    db.session.commit()
    log_admin_action(f"Approved flagged review {review_id}", "review")
    flash("Review approved and will now be visible.", "success")
    return redirect(url_for("auth.admin_moderation"))

@auth_bp.route("/admin/moderation/<int:review_id>/reject", methods=["POST"])
@admin_required
def reject_flagged_review(review_id):
    """Reject a flagged review"""
    from datetime import datetime
    review = Review.query.get_or_404(review_id)
    review.is_approved = False
    review.moderated_by_id = current_user.id
    review.moderated_at = datetime.utcnow()
    review.moderation_action = 'rejected'
    db.session.commit()
    log_admin_action(f"Rejected flagged review {review_id}", "review")
    flash("Review rejected and will not be visible.", "error")
    return redirect(url_for("auth.admin_moderation"))