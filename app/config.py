import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///scootermania.db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_TOKEN_SALT = os.getenv("API_TOKEN_SALT", "dev-api-salt")
    SCOOTER_UNLOCK_FEE = 2.50
    PRICE_PER_MINUTE = 0.35
    SWISS_TIMEZONE = "Europe/Zurich"
