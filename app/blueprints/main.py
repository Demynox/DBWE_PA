from flask import Blueprint, render_template
from flask_login import current_user

from ..models.ride import Ride
from ..models.scooter import Scooter

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    if current_user.is_authenticated:
        available_count = Scooter.query.filter_by(status="available").count()
        active_count = Ride.query.filter_by(status="active").count()
        latest_scooters = Scooter.query.order_by(Scooter.id.desc()).limit(3).all()
    else:
        available_count = None
        active_count = None
        latest_scooters = []

    return render_template(
        "index.html",
        available_count=available_count,
        active_count=active_count,
        latest_scooters=latest_scooters,
    )
