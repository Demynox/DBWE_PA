from decimal import Decimal, ROUND_HALF_UP

from flask import current_app


def calculate_ride_price(duration_minutes):
    unlock_fee = Decimal(str(current_app.config["SCOOTER_UNLOCK_FEE"]))
    price_per_minute = Decimal(str(current_app.config["PRICE_PER_MINUTE"]))
    minutes = Decimal(str(duration_minutes))
    total = unlock_fee + (minutes * price_per_minute)
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
