from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


STATUS_LABELS = {
    "available": "Verfügbar",
    "in_use": "In Benutzung",
    "maintenance": "In Wartung",
    "active": "Aktiv",
    "completed": "Abgeschlossen",
    "processed": "Verarbeitet",
}


def format_swiss_datetime(value):
    if not value:
        return "-"
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    try:
        local_zone = ZoneInfo("Europe/Zurich")
    except ZoneInfoNotFoundError:
        local_zone = timezone.utc
    local_value = value.astimezone(local_zone)
    return local_value.strftime("%d.%m.%Y %H:%M")


def format_swiss_currency(value):
    amount = float(value)
    return f"CHF {amount:,.2f}".replace(",", "'").replace(".", ",").replace("'", ".", 1)


def format_status_label(value):
    return STATUS_LABELS.get(value, value)
