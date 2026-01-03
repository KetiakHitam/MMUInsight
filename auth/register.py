import uuid
from flask import render_template, request, redirect, url_for, flash
from flask_babel import gettext as _
from flask_mail import Message
from . import auth_bp
from extensions import db, bcrypt, limiter, mail
from models import User


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def register():
    if request.method == "GET":
        return render_template("register.html") 

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not email or not password or not confirm_password:
        flash(_("All fields are required"), "error")
        return redirect(url_for("auth.register"))

    if email.endswith("@student.mmu.edu.my"):
        user_type = "student"
    elif email.endswith("@mmu.edu.my"):
        user_type = "lecturer"
    else:
        flash(_("Email must be an MMU address"), "error")
        return redirect(url_for("auth.register"))

    if password != confirm_password:
        flash(_("Passwords do not match"), "error")
        return redirect(url_for("auth.register"))
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash(_("An account with this email already exists"), "error")
        return redirect(url_for("auth.register"))

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    token = str(uuid.uuid4())

    user = User(
        email=email,
        password_hash=pw_hash,
        user_type=user_type,
        verification_token=token,
        is_verified=False
    )

    # Try to save user to database first
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(_("An error occurred while creating your account. Please try again."), "error")
        return redirect(url_for("auth.register"))
    
    # Then try to send verification email
    verification_url = url_for('auth.verify_email', token=token, _external=True)
    try:
        msg = Message(
            subject="Verify Your MMUInsight Account",
            recipients=[email],
            body=f"""Welcome to MMUInsight!

Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you did not create this account, please ignore this email.

Best regards,
The MMUInsight Team
""",
            html=f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #667eea;">Welcome to MMUInsight!</h2>
                <p>Please verify your email address by clicking the button below:</p>
                <p style="margin: 30px 0;">
                    <a href="{verification_url}" style="background-color: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email Address</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p style="color: #666; word-break: break-all;">{verification_url}</p>
                <p style="color: #666; font-size: 0.9em; margin-top: 40px;">
                    This link will expire in 24 hours.<br>
                    If you did not create this account, please ignore this email.
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
        flash(_("Account created! Please check your email to verify your account."), "success")
    except Exception as e:
        # Email failed but account was created - show verification link
        flash(f"Account created but email failed to send. Verification link: {verification_url}", "warning")
    
    return redirect(url_for("auth.login"))
