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
@admin_bp.route("/staff")
@login_required
@role_required("admin")
def staff():
    staff_list = User.query.filter_by(role="staff").all()
    return render_template("admin/staff.html", staff_list=staff_list)


@admin_bp.route("/staff/<int:user_id>/approve", methods=["POST"])
@login_required
@role_required("admin")
def approve_staff(user_id):
    staff_member = User.query.get_or_404(user_id)
    staff_member.status = "active"
    db.session.commit()
    flash(f"{staff_member.name} approved.", "success")
    return redirect(url_for("admin.staff"))


@admin_bp.route("/staff/<int:user_id>/blacklist", methods=["POST"])
@login_required
@role_required("admin")
def blacklist_staff(user_id):
    staff_member = User.query.get_or_404(user_id)
    staff_member.status = "blacklisted"
    db.session.commit()
    flash(f"{staff_member.name} blacklisted.", "info")
    return redirect(url_for("admin.staff"))

@admin_bp.route("/treks/<int:trek_id>/assign", methods=["GET", "POST"])
@login_required
@role_required("admin")
def assign_staff(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    available_staff = User.query.filter_by(role="staff", status="active").all()

    if request.method == "POST":
        staff_id = request.form.get("staff_id", type=int)
        trek.assigned_staff_id = staff_id if staff_id else None
        db.session.commit()
        flash(f"Staff assignment updated for '{trek.name}'.", "success")
        return redirect(url_for("admin.treks"))

    return render_template("admin/assign_staff.html", trek=trek, available_staff=available_staff)
@admin_bp.route("/users")
@login_required
@role_required("admin")
def users():
    search = request.args.get("search", "").strip()
    trekkers = User.query.filter_by(role="trekker")
    if search:
        trekkers = trekkers.filter(
            User.name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%")
        )
    trekkers = trekkers.all()
    return render_template("admin/users.html", trekkers=trekkers, search=search)


@admin_bp.route("/users/<int:user_id>/blacklist", methods=["POST"])
@login_required
@role_required("admin")
def blacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    user.status = "blacklisted"
    db.session.commit()
    flash(f"{user.name} has been blacklisted.", "info")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/unblacklist", methods=["POST"])
@login_required
@role_required("admin")
def unblacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    user.status = "active"
    db.session.commit()
    flash(f"{user.name} has been reinstated.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/bookings")
@login_required
@role_required("admin")
def bookings():
    all_bookings = Booking.query.all()
    return render_template("admin/bookings.html", bookings=all_bookings)


@admin_bp.route("/search")
@login_required
@role_required("admin")
def search():
    q = request.args.get("q", "").strip()
    treks, staff_results, trekker_results = [], [], []

    if q:
        treks = Trek.query.filter(
            Trek.name.ilike(f"%{q}%") | Trek.location.ilike(f"%{q}%")
        ).all()
        staff_results = User.query.filter(
            User.role == "staff",
            User.name.ilike(f"%{q}%") | User.email.ilike(f"%{q}%")
        ).all()
        trekker_results = User.query.filter(
            User.role == "trekker",
            User.name.ilike(f"%{q}%") | User.email.ilike(f"%{q}%")
        ).all()

    return render_template("admin/search.html", q=q,
                           treks=treks,
                           staff_results=staff_results,
                           trekker_results=trekker_results)