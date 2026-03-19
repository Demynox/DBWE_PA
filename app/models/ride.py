from ..extensions import db
from ..services.time_utils import now_in_app_timezone


class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    distance_km = db.Column(db.Float, nullable=False, default=0.0)
    duration_minutes = db.Column(db.Integer, nullable=False, default=0)
    total_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    start_latitude = db.Column(db.Float, nullable=False)
    start_longitude = db.Column(db.Float, nullable=False)
    end_latitude = db.Column(db.Float, nullable=True)
    end_longitude = db.Column(db.Float, nullable=True)
    started_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=now_in_app_timezone,
    )
    ended_at = db.Column(db.DateTime(timezone=True), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="active")
    scooter_id = db.Column(db.Integer, db.ForeignKey("scooter.id"), nullable=False)
    rider_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    scooter = db.relationship("Scooter", back_populates="rides")
    rider = db.relationship("User", back_populates="rides")
    payment_transaction = db.relationship(
        "PaymentTransaction", back_populates="ride", uselist=False
    )
