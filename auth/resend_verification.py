import uuid
from flask import request, redirect, url_for, flash, render_template
from flask_babel import gettext as _
from flask_mail import Message
from . import auth_bp
from extensions import db, limiter, mail
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
    
    token = str(uuid.uuid4())
    user.verification_token = token
    db.session.commit()
    
    verification_url = url_for('auth.verify_email', token=token, _external=True)
    
    try:
        msg = Message(
            subject="MMUInsight - Verify Your Account",
            recipients=[email],
            body=f"""Hello,

Here is your new verification link for MMUInsight:

{verification_url}

This link will expire in 24 hours.

If you did not request this, please ignore this email.

Best regards,
The MMUInsight Team
""",
            html=f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #667eea;">Email Verification</h2>
                <p>Here is your new verification link for MMUInsight:</p>
                <p style="margin: 30px 0;">
                    <a href="{verification_url}" style="background-color: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email Address</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p style="color: #666; word-break: break-all;">{verification_url}</p>
                <p style="color: #666; font-size: 0.9em; margin-top: 40px;">
                    This link will expire in 24 hours.<br>
                    If you did not request this, please ignore this email.
                </p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="color: #999; font-size: 0.8em;">
                    Best regards,<br>
                    The MMUInsight Team
                </p>
            </body>
            </html>
            """
        )
        mail.send(msg)
        flash(_("If an unverified account exists with this email, a verification link has been sent."), "info")
    except Exception as e:
        flash(f"Email failed to send. Verification link: {verification_url}", "warning")
    
    return redirect(url_for("auth.login"))
