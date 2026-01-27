import uuid
import re
from flask import render_template, request, redirect, url_for, flash
from flask_babel import gettext as _
from . import auth_bp
from extensions import db, bcrypt, limiter
from models import User, Lecturer

def validate_password_strength(password):
     """Validate password meets security requirements"""
     if len(password) < 8:
         return False, "Password must be at least 8 characters long"
     if not re.search(r'[A-Z]', password):
         return False, "Password must contain at least one uppercase letter"
     if not re.search(r'[a-z]', password):
         return False, "Password must contain at least one lowercase letter"
     if not re.search(r'[0-9]', password):
         return False, "Password must contain at least one number"
     if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
         return False, "Password must contain at least one special character (!@#$%^&*)"
     return True, "Password is strong"


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
    
    # Validate password strength
    is_valid, message = validate_password_strength(password)
    if not is_valid:
        flash(_(message), "error")
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
        is_verified=True
    )

    # Try to save user to database first
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(_("An error occurred while creating your account. Please try again."), "error")
        return redirect(url_for("auth.register"))
    
    # Auto-claim lecturer profile if email matches
    if user_type == "lecturer":
        lecturer = Lecturer.query.filter_by(email=email).first()
        if lecturer and not lecturer.claimed_by_user_id:
            lecturer.claimed_by_user_id = user.id
            try:
                db.session.commit()
                flash(_("Your lecturer profile has been automatically claimed!"), "success")
            except Exception as e:
                db.session.rollback()
    
    flash(_("Account created successfully! You can now log in."), "success")
    return redirect(url_for("auth.login"))
