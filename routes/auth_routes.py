from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from models import User
from werkzeug.security import check_password_hash
from forms.WTForm import LoginForm


auth_bp = Blueprint("auth", __name__)


# -----------------------------
# ADMIN LOGIN
# -----------------------------
@auth_bp.route("/admin", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.admin_dashboard"))


    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Welcome back, you are now logged in.", "success")
            return redirect(url_for("dashboard.admin_dashboard"))
        else:
            if not user:
                flash("User not registered — please contact site administrator.", "error")
            else:
                flash("Invalid password. Please try again.", "error")


    return render_template("admin/admin_login.html", form=form)




# -----------------------------
# ADMIN LOGOUT
# -----------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.admin_login"))
