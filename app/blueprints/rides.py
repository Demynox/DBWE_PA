from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models.payment_transaction import PaymentTransaction
from ..models.ride import Ride
from ..models.scooter import Scooter
from ..services.pricing import calculate_ride_price
from ..services.time_utils import ensure_app_timezone, now_in_app_timezone

bp = Blueprint("rides", __name__)


def _ensure_rider():
    if current_user.role != "rider":
        flash("Diese Funktion steht nur für Fahrerprofile zur Verfügung.", "error")
        return redirect(url_for("scooters.list_scooters"))
    if not current_user.payment_method:
        flash("Bitte hinterlege zuerst ein gültiges Zahlungsmittel.", "error")
        return redirect(url_for("auth.register"))
    return None


@bp.route("/")
@login_required
def list_rides():
    if current_user.can_manage_scooters():
        rides = Ride.query.order_by(Ride.id.desc()).all()
    else:
        rides = Ride.query.filter_by(rider_id=current_user.id).order_by(Ride.id.desc()).all()
    return render_template("rides/list.html", rides=rides)


@bp.route("/scan", methods=["GET", "POST"])
@login_required
def scan_qr():
    access_error = _ensure_rider()
    if access_error:
        return access_error

    if request.method == "POST":
        qr_code = request.form.get("qr_code", "").strip().upper()
        scooter = Scooter.query.filter_by(code=qr_code).first()
        if not scooter:
            flash("Für den eingegebenen Code wurde kein Fahrzeug gefunden.", "error")
            return render_template("rides/scan.html")
        return render_template("rides/scan.html", scooter=scooter)

    return render_template("rides/scan.html")


@bp.route("/start/<int:scooter_id>", methods=["POST"])
@login_required
def start_ride(scooter_id):
    access_error = _ensure_rider()
    if access_error:
        return access_error

    scooter = db.get_or_404(Scooter, scooter_id)

    if scooter.status != "available":
        flash("Dieses Fahrzeug ist aktuell nicht verfügbar.", "error")
        return redirect(url_for("scooters.list_scooters"))

    active_ride = Ride.query.filter_by(rider_id=current_user.id, status="active").first()
    if active_ride:
        flash("Es ist bereits eine aktive Fahrt mit deinem Konto verknüpft.", "error")
        return redirect(url_for("rides.list_rides"))

    ride = Ride(
        scooter=scooter,
        rider=current_user,
        start_latitude=scooter.latitude,
        start_longitude=scooter.longitude,
    )
    scooter.status = "in_use"
    db.session.add(ride)
    db.session.commit()
    flash("Die Fahrt wurde gestartet.", "success")
    return redirect(url_for("rides.list_rides"))


@bp.route("/end/<int:ride_id>", methods=["GET", "POST"])
@login_required
def end_ride(ride_id):
    access_error = _ensure_rider()
    if access_error:
        return access_error

    ride = db.get_or_404(Ride, ride_id)

    if ride.rider_id != current_user.id or ride.status != "active":
        flash("Diese Fahrt kann derzeit nicht beendet werden.", "error")
        return redirect(url_for("rides.list_rides"))

    if request.method == "POST":
        try:
            distance_km = float(request.form.get("distance_km", "0"))
            end_latitude = float(request.form.get("end_latitude", ride.scooter.latitude))
            end_longitude = float(request.form.get("end_longitude", ride.scooter.longitude))
        except ValueError:
            flash("Bitte prüfe die Angaben für Distanz und Position.", "error")
            return render_template("rides/end.html", ride=ride)

        if distance_km <= 0:
            flash("Die zurückgelegte Distanz muss mehr als 0 betragen.", "error")
            return render_template("rides/end.html", ride=ride)

        ended_at = now_in_app_timezone()
        started_at = ensure_app_timezone(ride.started_at)
        duration_seconds = max(60, int((ended_at - started_at).total_seconds()))
        duration_minutes = max(1, (duration_seconds + 59) // 60)

        ride.distance_km = distance_km
        ride.end_latitude = end_latitude
        ride.end_longitude = end_longitude
        ride.ended_at = ended_at
        ride.duration_minutes = duration_minutes
        ride.total_price = calculate_ride_price(duration_minutes)
        ride.status = "completed"

        ride.scooter.latitude = end_latitude
        ride.scooter.longitude = end_longitude
        ride.scooter.status = "available"
        ride.scooter.battery_level = max(0, ride.scooter.battery_level - int(distance_km * 8))

        payment = PaymentTransaction(
            amount=ride.total_price,
            payment_method=current_user.payment_method,
            status="processed",
            ride=ride,
            user=current_user,
        )
        db.session.add(payment)

        db.session.commit()
        flash("Die Fahrt wurde abgeschlossen und abgerechnet.", "success")
        return redirect(url_for("rides.list_rides"))

    return render_template("rides/end.html", ride=ride)
