from urllib.parse import quote
from datetime import datetime
from app import constants
import unicodedata
import secrets
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
def slugify(
    text,
    content_id=None,
    word_separator="-",
    max_length=240,
):
    # Remove any diacritics (accents) from the text
    text = (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("utf-8")
    )

    # Convert the text to lowercase and replace spaces with the word separator
    text = re.sub(r"\s+", word_separator, text.lower())

    # Remove any non-word characters (except the word separator)
    text = re.sub(r"[^a-zA-Z0-9" + word_separator + r"]", "", text)

    # Truncate the slug if it exceeds the max_length
    if max_length and len(text) > max_length:
        text = text[:max_length].rstrip(word_separator)

    # Add content id part if specified
    if content_id:
        text += word_separator + content_id[:6]

    # Remove trailing word separator
    text = text.strip(word_separator)

    # Remove extra characters at the start and end
    text = text.strip("_")

    # Remove duplicate separators
    text = re.sub(word_separator + r"+", word_separator, text)

    # URL-encode the slug to handle special characters and spaces
    text = quote(text)

    # Fallback if text is empty
    if not text:
        text = secrets.token_urlsafe(32)

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
