from flask import Flask

from .config import Config
from .extensions import db, login_manager, migrate
from .services.formatting import format_status_label


def create_app(test_config=None):
    # Die App-Factory erlaubt dieselbe Anwendung für Entwicklung, Tests und Produktion.
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .models import api_token, payment_transaction, ride, scooter, user

    from .blueprints.api import bp as api_bp
    from .blueprints.auth import bp as auth_bp
    from .blueprints.main import bp as main_bp
    from .blueprints.rides import bp as rides_bp
    from .blueprints.scooters import bp as scooters_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(scooters_bp, url_prefix="/scooters")
    app.register_blueprint(rides_bp, url_prefix="/rides")
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.context_processor
    def inject_prices():
        # Diese Werte werden in mehreren Templates benötigt und deshalb zentral bereitgestellt.
        return {
            "unlock_fee": app.config["SCOOTER_UNLOCK_FEE"],
            "price_per_minute": app.config["PRICE_PER_MINUTE"],
            "format_status_label": format_status_label,
        }

    return app
