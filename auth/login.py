from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user
from flask_babel import gettext as _
from . import auth_bp
from extensions import bcrypt, limiter
from models import User

@auth_bp.route("/login", methods=["GET", "POST"])
# @limiter.limit("5 per minute")  # Disabled for development
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    error_message = _("Your login credentials don't match an account in our system")

    if not email or not password:
        flash(error_message, "error")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()


    if user and bcrypt.check_password_hash(user.password_hash, password):
        login_user(user, remember=True)
        flash(_("Login successful!"), "success")
        return redirect(url_for('index'))

    flash(error_message, "error")
    return redirect(url_for("auth.login"))

