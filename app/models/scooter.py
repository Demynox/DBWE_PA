from ..extensions import db
from ..services.time_utils import now_in_app_timezone


class Scooter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    battery_level = db.Column(db.Integer, nullable=False, default=100)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    city = db.Column(db.String(80), nullable=False, default="Zürich")
    status = db.Column(db.String(20), nullable=False, default="available")
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=now_in_app_timezone,
    )
    provider_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    provider = db.relationship("User", back_populates="scooters")
    rides = db.relationship("Ride", back_populates="scooter", lazy=True)
