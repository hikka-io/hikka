from unicodedata import normalize
from datetime import datetime
from app import constants
import orjson
import math
import re


# Split list into chunks
def chunkify(lst, size):
    return [lst[i : i + size] for i in range(0, len(lst), size)]


# Dump dict using orjson
def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


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
def pagination(page, limit=constants.SEARCH_RESULT_LIMIT):
    offset = (limit * (page)) - limit

    return limit, offset


# Helper function to make pagication dict for api
def pagination_dict(total, page, limit):
    return {
        "pages": math.ceil(total / limit),
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
