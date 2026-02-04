from flask import render_template, request, redirect, url_for, flash
from flask_babel import gettext as _
from . import auth_bp
from extensions import db
from models import User

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html")

    # For password reset, users must contact admin
    flash(_("To reset your password, please email ISAC.MEGAT.AZLAN@student.mmu.edu.my from the email address associated with your account for security verification."), "info")
    return redirect(url_for("auth.login"))

