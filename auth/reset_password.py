import uuid
from flask import current_app, render_template, request, url_for
from flask_mail import Message
from . import auth_bp
from extensions import bcrypt, db, mail
from models import User
from datetime import datetime, timedelta

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html")

    email = request.form.get("email")

    if not email:
        return "Please enter your email."

    user = User.query.filter_by(email=email).first()

    if not user:
        return "If this email exists, a reset link has been generated."

    token = str(uuid.uuid4())
    user.reset_token = token
    user.reset_token_created_at = datetime.utcnow()
    db.session.commit()

    reset_url = url_for("auth.reset_password", token=token, _external=True)
    message_text = "If this email exists, a reset link has been sent."

    if current_app.config.get("MAIL_USERNAME") and current_app.config.get("MAIL_PASSWORD"):
        try:
            msg = Message(
                subject="MMUInsight Password Reset",
                recipients=[email],
                body=(
                    "A password reset was requested for your MMUInsight account.\n\n"
                    f"Reset your password using this link (expires in 10 minutes):\n{reset_url}\n\n"
                    "If you did not request this, you can ignore this email."
                ),
            )
            mail.send(msg)
        except Exception:
            current_app.logger.exception("Failed to send password reset email")
    else:
        # dev convenience: show the link only when running in debug.
        if current_app.debug or current_app.config.get("DEBUG") is True:
            return f"Password reset link (debug): {reset_url}"

    return message_text


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()

    if not user:
        return "Invalid or expired reset link."

    if not user.reset_token_created_at:
        return "Invalid or expired token"

    if datetime.utcnow() - user.reset_token_created_at > timedelta(minutes=10):
        return "Reset token has expired. Please request a new one."

    if request.method == "GET":
        return render_template("reset_password.html")

    new_pw = request.form.get("password")
    confirm_pw = request.form.get("confirm_password")

    if not new_pw or not confirm_pw:
        return "Please fill in both password fields."

    if new_pw != confirm_pw:
        return "Passwords do not match."

    # clear token immediately after validation passes
    user.reset_token = None
    user.reset_token_created_at = None
    
    user.password_hash = bcrypt.generate_password_hash(new_pw).decode("utf-8")
    db.session.commit()

    return "Password reset successfully. You can now log in."
