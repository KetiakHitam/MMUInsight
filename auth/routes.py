from flask import render_template, redirect, url_for, flash
from . import auth_bp
from auth.decorators import login_required, admin_required
from models import User, Report, Review
from extensions import db

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
    )

@auth_bp.route("/admin/users")
@admin_required
def admin_users():
    users = User.query.all()
    return render_template("admin_users.html", users=users)

@auth_bp.route("/admin/user/<int:user_id>/verify")
@admin_required
def admin_verify_user(user_id):
    user = User.query.get(user_id)
    current_user = User.query.filter_by(id=1).first()
    if user and current_user and current_user.can_manage_user(user):
        user.is_verified = True
        db.session.commit()
    return redirect(url_for("auth.admin_users"))

@auth_bp.route("/admin/user/<int:user_id>/make-admin")
@admin_required
def admin_make_admin(user_id):
    from flask_login import current_user
    user = User.query.get(user_id)
    if user and current_user.can_change_role(user, 'ADMIN'):
        user.role = 'ADMIN'
        db.session.commit()
        flash(f"{user.email} is now an ADMIN", "success")
    else:
        flash("You don't have permission to assign this role", "danger")
    return redirect(url_for("auth.admin_users"))

@auth_bp.route("/admin/user/<int:user_id>/make-mod")
@admin_required
def admin_make_mod(user_id):
    from flask_login import current_user
    user = User.query.get(user_id)
    if user and current_user.can_change_role(user, 'MOD'):
        user.role = 'MOD'
        db.session.commit()
        flash(f"{user.email} is now a MOD", "success")
    else:
        flash("You don't have permission to assign this role", "danger")
    return redirect(url_for("auth.admin_users"))

@auth_bp.route("/admin/user/<int:user_id>/remove-role")
@admin_required
def admin_remove_role(user_id):
    from flask_login import current_user
    user = User.query.get(user_id)
    if user and current_user.can_manage_user(user) and not user.is_owner():
        user.role = None
        db.session.commit()
        flash(f"Role removed from {user.email}", "success")
    else:
        flash("You don't have permission to remove this role", "danger")
    return redirect(url_for("auth.admin_users"))

@auth_bp.route("/admin/user/<int:user_id>/suspend")
@admin_required
def admin_suspend_user(user_id):
    from flask_login import current_user
    user = User.query.get(user_id)
    if user and current_user.can_suspend_user(user):
        user.is_verified = False    
        db.session.commit()
        flash(f"{user.email} has been suspended", "success")
    else:
        flash("You don't have permission to suspend this user", "danger")
    return redirect(url_for("auth.admin_users"))

@auth_bp.route("/admin/user/<int:user_id>/delete")
@admin_required
def admin_delete_user(user_id):
    from flask_login import current_user
    user = User.query.get(user_id)
    if user and current_user.can_delete_user(user):
        db.session.delete(user)
        db.session.commit()
        flash(f"{user.email} has been deleted", "success")
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
        flash("Report dismissed", "success")
    return redirect(url_for("auth.admin_reports"))

@auth_bp.route("/admin/report/<int:report_id>/delete-review")
@admin_required
def admin_delete_reported_review(report_id):
    report = Report.query.get(report_id)
    if report:
        review = report.review
        db.session.delete(review)
        report.status = 'deleted'
        db.session.commit()
        flash("Review deleted", "success")
    return redirect(url_for("auth.admin_reports"))