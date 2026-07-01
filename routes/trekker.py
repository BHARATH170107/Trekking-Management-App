from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from decorators import role_required
from models import Trek, Booking, User

trekker_bp = Blueprint("trekker", __name__, url_prefix="/trekker")


@trekker_bp.route("/dashboard")
@login_required
@role_required("trekker")
def dashboard():
    open_treks = Trek.query.filter_by(status="Open").all()
    my_bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template("trekker/dashboard.html", treks=open_treks, bookings=my_bookings)


@trekker_bp.route("/trek/<int:trek_id>/book", methods=["POST"])
@login_required
@role_required("trekker")
def book_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    # Rule 1: trek must be Open
    if trek.status != "Open":
        flash("This trek is not open for booking.", "danger")
        return redirect(url_for("trekker.dashboard"))

    # Rule 2: must have available slots
    if trek.available_slots <= 0:
        flash("Sorry, this trek is fully booked.", "danger")
        return redirect(url_for("trekker.dashboard"))

    # Rule 3: user can't book the same trek twice
    existing = Booking.query.filter_by(
        user_id=current_user.id,
        trek_id=trek_id
    ).first()
    if existing:
        flash("You have already booked this trek.", "warning")
        return redirect(url_for("trekker.dashboard"))

    # All checks passed — create the booking
    booking = Booking(user_id=current_user.id, trek_id=trek_id)
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()
    flash(f"Successfully booked '{trek.name}'!", "success")
    return redirect(url_for("trekker.dashboard"))


@trekker_bp.route("/treks")
@login_required
@role_required("trekker")
def search_treks():
    difficulty = request.args.get("difficulty", "")
    location = request.args.get("location", "").strip()

    query = Trek.query.filter_by(status="Open")

    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))

    treks = query.all()
    return render_template("trekker/search.html", treks=treks,
                           difficulty=difficulty, location=location)


@trekker_bp.route("/history")
@login_required
@role_required("trekker")
def history():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template("trekker/history.html", bookings=bookings)


@trekker_bp.route("/profile", methods=["GET", "POST"])
@login_required
@role_required("trekker")
def profile():
    if request.method == "POST":
        current_user.name = request.form.get("name", "").strip()
        current_user.contact = request.form.get("contact", "").strip()
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("trekker.profile"))
    return render_template("trekker/profile.html", user=current_user)