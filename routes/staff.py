from flask import Blueprint, render_template
from flask_login import login_required, current_user

from decorators import role_required
from models import Trek

staff_bp = Blueprint("staff", __name__, url_prefix="/staff")


@staff_bp.route("/dashboard")
@login_required
@role_required("staff")
def dashboard():
    assigned_treks = Trek.query.filter_by(assigned_staff_id=current_user.id).all()
    return render_template("staff/dashboard.html", treks=assigned_treks)

# TODO (next steps for you to build):
#   - /staff/trek/<id>/update  -> edit slots / status (Open/Closed)
#   - /staff/trek/<id>/participants -> list users booked on a trek
