from flask import Blueprint, render_template
from flask_login import login_required, current_user

from decorators import role_required
from models import Trek, Booking

trekker_bp = Blueprint("trekker", __name__, url_prefix="/trekker")


@trekker_bp.route("/dashboard")
@login_required
@role_required("trekker")
def dashboard():
    open_treks = Trek.query.filter_by(status="Open").all()
    my_bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template("trekker/dashboard.html", treks=open_treks, bookings=my_bookings)

# TODO (next steps for you to build):
#   - /trekker/treks            -> search/filter treks by difficulty, location
#   - /trekker/trek/<id>/book   -> book a trek (check available_slots > 0!)
#   - /trekker/history          -> past bookings (Completed/Cancelled)
#   - /trekker/profile          -> edit profile
