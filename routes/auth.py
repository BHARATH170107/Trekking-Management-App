from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required

from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        contact = request.form.get("contact", "").strip()
        role = request.form.get("role")  # only 'staff' or 'trekker' allowed here

        if role not in ("staff", "trekker"):
            flash("Invalid role selection.", "danger")
            return redirect(url_for("auth.register"))

        if not name or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("That email is already registered.", "danger")
            return redirect(url_for("auth.register"))

        # Staff need admin approval before they can log in; trekkers don't.
        status = "pending" if role == "staff" else "active"

        user = User(name=name, email=email, contact=contact, role=role, status=status)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        if role == "staff":
            flash("Registered! Your account needs admin approval before you can log in.", "info")
        else:
            flash("Registration successful. You can log in now.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        if user.status == "blacklisted":
            flash("This account has been blacklisted. Contact admin.", "danger")
            return redirect(url_for("auth.login"))

        if user.role == "staff" and user.status == "pending":
            flash("Your staff account is awaiting admin approval.", "warning")
            return redirect(url_for("auth.login"))

        login_user(user)

        if user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        elif user.role == "staff":
            return redirect(url_for("staff.dashboard"))
        else:
            return redirect(url_for("trekker.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))
