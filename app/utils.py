from pydantic.datetime_parse import parse_datetime
from unicodedata import normalize
from datetime import datetime
import math
import re


# Quick hack to make FastAPI display datetime as timestamp
class Datetime(int):
    @classmethod
    def __get_validators__(cls):
        yield parse_datetime
        yield cls.validate

    @classmethod
    def validate(cls, value) -> int:
        return int(value.timestamp())


# Generate URL safe slug
def slugify(text, content_id=None):
    text = normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[-\s]+", "-", text)
    text = text.strip("-")

    if content_id:
        text += "-" + content_id[:6]

    return text


# Convest timestamp to UTC datetime
def from_timestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp) if timestamp else None


# Convert datetime to timestamp
def to_timestamp(date):
    return int(date.timestamp()) if date else None


# Helper function for toroise pagination
def pagination(page, size=20):
    limit = size
    offset = (limit * (page)) - limit

    return limit, offset, size


# Helper function to make pagication dict for api
def pagination_dict(total, page, size):
    return {
        "pages": math.ceil(total / size),
        "total": total,
        "page": page,
    }


# Convert month to season str
def get_season(date):
    season_map = {
        12: "winter",
        1: "winter",
        2: "winter",
        3: "spring",
        4: "spring",
        5: "spring",
        6: "summer",
        7: "summer",
        8: "summer",
        9: "fall",
        10: "fall",
        11: "fall",
    }

    return season_map.get(date.month) if date else None
