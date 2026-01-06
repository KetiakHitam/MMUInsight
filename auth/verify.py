from flask import redirect, url_for, flash, render_template
from flask_babel import gettext as _
from . import auth_bp
from extensions import db
from models import User
from datetime import datetime, timedelta

@auth_bp.route("/verify/<token>")
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()

    if not user:
        flash(_("Invalid or expired verification link"), "error")
        return redirect(url_for("auth.login"))
    
    if user.is_verified:
        flash(_("Email already verified. Please log in."), "info")
        return redirect(url_for("auth.login"))

    # Check if token has expired (24 hours)
    if not user.verification_token_created_at:
        flash(_("Invalid or expired verification link"), "error")
        return redirect(url_for("auth.login"))
    
    if datetime.utcnow() - user.verification_token_created_at > timedelta(hours=24):
        flash(_("Verification link has expired. Please register again."), "error")
        user.verification_token = None
        db.session.commit()
        return redirect(url_for("auth.register"))

    # Verify the user
    user.is_verified = True
    user.verification_token = None
    user.verification_token_created_at = None
    db.session.commit()

    flash(_("Email verified successfully! You can now log in."), "success")
    return redirect(url_for("auth.login"))