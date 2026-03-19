from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from ..models.user import User
from ..models.ride import Ride
from ..models.scooter import Scooter
from ..services.auth import create_api_token_for_user, get_user_by_token
from ..services.formatting import format_swiss_datetime

bp = Blueprint("api", __name__)


@bp.before_request
def authenticate_api():
    if request.endpoint in {"api.health", "api.create_token"}:
        return None

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "API-Token fehlt."}), 401

    token = auth_header.replace("Bearer ", "", 1).strip()
    user = get_user_by_token(token)
    if not user:
        return jsonify({"error": "Ungültiger API-Token."}), 401

    return None


@bp.route("/health")
def health():
    return jsonify({"status": "ok", "service": "Scootermania API"})


@bp.route("/auth/token", methods=["POST"])
def create_token():
    payload = request.get_json(silent=True) or {}
    login_value = str(payload.get("login", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))
    identifier = login_value or email or username

    if not identifier or not password:
        return jsonify({"error": "Benutzername oder E-Mail sowie Passwort sind erforderlich."}), 400

    user = User.query.filter(
        or_(
            User.email == identifier.lower(),
            User.username == identifier,
        )
    ).first()
    if user is None or not user.check_password(password):
        return jsonify({"error": "Login fehlgeschlagen."}), 401

    token = create_api_token_for_user(user)
    return jsonify(
        {
            "token": token,
            "token_type": "Bearer",
            "user": {
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
        }
    )


@bp.route("/scooters", methods=["GET"])
def scooters():
    # Der Endpunkt liefert die wichtigsten Fahrzeugdaten für externe Clients.
    scooters = Scooter.query.order_by(Scooter.id.desc()).all()
    data = [
        {
            "id": scooter.id,
            "code": scooter.code,
            "model_name": scooter.model_name,
            "battery_level": scooter.battery_level,
            "city": scooter.city,
            "status": scooter.status,
            "provider": scooter.provider.username,
            "latitude": scooter.latitude,
            "longitude": scooter.longitude,
        }
        for scooter in scooters
    ]
    return jsonify(data)


@bp.route("/rides", methods=["GET"])
def rides():
    # Die Fahrten-API zeigt die wichtigsten fachlichen Resultate inklusive Zahlung an.
    rides = Ride.query.order_by(Ride.id.desc()).all()
    data = [
        {
            "id": ride.id,
            "scooter_code": ride.scooter.code,
            "rider": ride.rider.username,
            "status": ride.status,
            "distance_km": ride.distance_km,
            "duration_minutes": ride.duration_minutes,
            "total_price": float(ride.total_price),
            "payment_status": ride.payment_transaction.status if ride.payment_transaction else None,
            "started_at": format_swiss_datetime(ride.started_at),
            "ended_at": format_swiss_datetime(ride.ended_at) if ride.ended_at else None,
        }
        for ride in rides
    ]
    return jsonify(data)
