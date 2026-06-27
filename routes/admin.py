from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from decorators import role_required
from models import User, Trek, Booking

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    stats = {
        "total_treks": Trek.query.count(),
        "total_trekkers": User.query.filter_by(role="trekker").count(),
        "total_staff": User.query.filter_by(role="staff").count(),
        "total_bookings": Booking.query.count(),
        "pending_staff": User.query.filter_by(role="staff", status="pending").count(),
    }
    return render_template("admin/dashboard.html", stats=stats)
    
# TODO (next steps for you to build):
#   - /admin/treks            -> list/create/edit/delete treks
#   - /admin/staff             -> list staff, approve/blacklist
#   - /admin/staff/assign      -> assign staff to a trek
#   - /admin/users             -> list/search/blacklist trekkers
#   - /admin/bookings          -> view all bookings
@admin_bp.route("/treks")
@login_required
@role_required("admin")
def treks():
    all_treks = Trek.query.all()
    return render_template("admin/treks.html", treks=all_treks)


@admin_bp.route("/treks/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def new_trek():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        difficulty = request.form.get("difficulty")
        total_slots = request.form.get("total_slots", type=int)
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        if not name or not location or not total_slots:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("admin.new_trek"))

        trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            total_slots=total_slots,
            available_slots=total_slots,
            status="Pending",
            start_date=datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None,
            end_date=datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None,
        )
        db.session.add(trek)
        db.session.commit()
        flash(f"Trek '{trek.name}' created.", "success")
        return redirect(url_for("admin.treks"))

    return render_template("admin/trek_form.html", trek=None)


@admin_bp.route("/treks/<int:trek_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    if request.method == "POST":
        trek.name = request.form.get("name", "").strip()
        trek.location = request.form.get("location", "").strip()
        trek.difficulty = request.form.get("difficulty")
        trek.total_slots = request.form.get("total_slots", type=int)
        trek.status = request.form.get("status")

        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        trek.start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        trek.end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

        db.session.commit()
        flash(f"Trek '{trek.name}' updated.", "success")
        return redirect(url_for("admin.treks"))

    return render_template("admin/trek_form.html", trek=trek)


@admin_bp.route("/treks/<int:trek_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    flash(f"Trek '{trek.name}' deleted.", "info")
    return redirect(url_for("admin.treks"))