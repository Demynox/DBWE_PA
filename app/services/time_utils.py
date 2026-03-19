from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import current_app


def get_app_timezone():
    timezone_name = current_app.config.get("SWISS_TIMEZONE", "Europe/Zurich")
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return timezone.utc


def now_in_app_timezone():
    return datetime.now(get_app_timezone())


def ensure_app_timezone(value):
    if value is None:
        return None

    app_timezone = get_app_timezone()
    if value.tzinfo is None:
        return value.replace(tzinfo=app_timezone)
    return value.astimezone(app_timezone)
