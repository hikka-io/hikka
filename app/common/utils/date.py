from zoneinfo import ZoneInfo
from datetime import timezone


def kyiv_to_utc(date):
    return (
        date.replace(tzinfo=ZoneInfo("Europe/Kyiv"))
        .astimezone(timezone.utc)
        .replace(tzinfo=None)
    )


def utc_to_kyiv(date):
    return (
        date.replace(tzinfo=timezone.utc)
        .astimezone(ZoneInfo("Europe/Kyiv"))
        .replace(tzinfo=None)
    )


def get_month(date):
    return utc_to_kyiv(date).strftime("%B").lower()
