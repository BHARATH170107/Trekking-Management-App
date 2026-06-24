from flask import Blueprint, render_template
from flask_login import login_required

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
