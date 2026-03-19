from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db, login_manager
from ..services.time_utils import now_in_app_timezone


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False, default="")
    last_name = db.Column(db.String(80), nullable=False, default="")
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="rider")
    payment_method = db.Column(db.String(120), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=now_in_app_timezone,
    )

    scooters = db.relationship("Scooter", back_populates="provider", lazy=True)
    rides = db.relationship("Ride", back_populates="rider", lazy=True)
    api_tokens = db.relationship("ApiToken", back_populates="user", lazy=True)
    payment_transactions = db.relationship(
        "PaymentTransaction", back_populates="user", lazy=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can_manage_scooters(self):
        return self.role in {"provider", "admin"}

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
