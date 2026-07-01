from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from decorators import role_required
from models import Trek, Booking, User

staff_bp = Blueprint("staff", __name__, url_prefix="/staff")


@staff_bp.route("/dashboard")
@login_required
@role_required("staff")
def dashboard():
    assigned_treks = Trek.query.filter_by(assigned_staff_id=current_user.id).all()
    return render_template("staff/dashboard.html", treks=assigned_treks)


@staff_bp.route("/trek/<int:trek_id>/update", methods=["GET", "POST"])
@login_required
@role_required("staff")
def update_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    # Security check: only the assigned staff can manage this trek
    if trek.assigned_staff_id != current_user.id:
        flash("You are not assigned to this trek.", "danger")
        return redirect(url_for("staff.dashboard"))

    if request.method == "POST":
        new_slots = request.form.get("available_slots", type=int)
        new_status = request.form.get("status")

        if new_slots is not None and new_slots >= 0:
            trek.available_slots = new_slots
        trek.status = new_status

        db.session.commit()
        flash(f"Trek '{trek.name}' updated.", "success")
        return redirect(url_for("staff.dashboard"))

    return render_template("staff/update_trek.html", trek=trek)


@staff_bp.route("/trek/<int:trek_id>/participants")
@login_required
@role_required("staff")
def participants(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    # Security check: only assigned staff can view participants
    if trek.assigned_staff_id != current_user.id:
        flash("You are not assigned to this trek.", "danger")
        return redirect(url_for("staff.dashboard"))

    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    return render_template("staff/participants.html", trek=trek, bookings=bookings)