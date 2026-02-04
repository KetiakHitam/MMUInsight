from flask import request, redirect, url_for, flash, render_template
from flask_babel import gettext as _
from . import auth_bp
from extensions import db, limiter
from models import User

@auth_bp.route("/resend-verification-page", methods=["GET"])
def resend_verification_page():
    """Display the resend verification email page"""
    return render_template("resend_verification.html")

@auth_bp.route("/resend-verification", methods=["POST"])
@limiter.limit("3 per hour")
def resend_verification():
    email = request.form.get("email", "").strip()
    
    if not email:
        flash(_("Please provide an email address"), "error")
        return redirect(url_for("auth.login"))
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        flash(_("If an unverified account exists with this email, a verification link has been sent."), "info")
        return redirect(url_for("auth.login"))
    
    if user.is_verified:
        flash(_("This account is already verified. Please log in."), "info")
        return redirect(url_for("auth.login"))
    
    # Auto-verify account (email disabled)
    user.is_verified = True
    db.session.commit()
    
    flash(_("Account verified! You can now log in."), "info")
    return redirect(url_for("auth.login"))
