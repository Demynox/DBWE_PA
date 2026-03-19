from ..extensions import db


class PaymentTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="processed")
    ride_id = db.Column(db.Integer, db.ForeignKey("ride.id"), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    ride = db.relationship("Ride", back_populates="payment_transaction")
    user = db.relationship("User", back_populates="payment_transactions")
