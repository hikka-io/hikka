from functools import lru_cache
from urllib.parse import quote
from dynaconf import Dynaconf
from datetime import timezone
from datetime import datetime
from app import constants
import unicodedata
import aiohttp
import secrets
import bcrypt
import math
import re


# Get bcrypt hash of password
def hashpwd(password: str) -> str:
    return bcrypt.hashpw(str.encode(password), bcrypt.gensalt()).decode()


# Check bcrypt password hash
def checkpwd(password: str, bcrypt_hash: str | None) -> bool:
    if bcrypt_hash:
        return bcrypt.checkpw(str.encode(password), str.encode(bcrypt_hash))

    return False


def new_token():
    """Genereate new random token"""

    return secrets.token_urlsafe(32)


@lru_cache()
def get_settings():
    """Returns lru cached system settings"""

    return Dynaconf(
        settings_files=["settings.toml"],
        default_env="default",
        environments=True,
    )


# Split list into chunks
def chunkify(lst, size):
    return [lst[i : i + size] for i in range(0, len(lst), size)]


# Generate URL safe slug
def slugify(
    text,
    content_id=None,
    max_length=240,
):
    # This used to be optional argument
    # But if we pass special characters like "?" it will break regex module
    # So it's hardcoded to "-" for the time being
    word_separator = "-"

    # https://zakon.rada.gov.ua/laws/show/55-2010-%D0%BF
    transliterate = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "h",
        "ґ": "g",
        "д": "d",
        "е": "e",
        "є": "ye",
        "ж": "zh",
        "з": "z",
        "и": "y",
        "і": "i",
        "ї": "yi",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "kh",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "shch",
        "ю": "yu",
        "я": "ya",
    }

    # Pass trough text and replace cyrillic characters according to
    # official Ukrainian transliteration
    text = "".join(
        transliterate[letter.lower()]
        if letter.lower() in transliterate
        else letter
        for letter in text
    )

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
        # 22 characters (16 bytes)
        text = secrets.token_urlsafe(16)

    return text


# Convest timestamp to UTC datetime
def from_timestamp(timestamp: int):
    return datetime.utcfromtimestamp(timestamp) if timestamp else None


# Convert datetime to timestamp
def to_timestamp(date: datetime | None) -> int | None:
    date = date.replace(tzinfo=timezone.utc) if date else date
    return int(date.timestamp()) if date else None


# Helper function for pagination
def pagination(page, size=constants.SEARCH_RESULT_SIZE):
    offset = (size * (page)) - size

    return size, offset


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
        12: constants.SEASON_WINTER,
        1: constants.SEASON_WINTER,
        2: constants.SEASON_WINTER,
        3: constants.SEASON_SPRING,
        4: constants.SEASON_SPRING,
        5: constants.SEASON_SPRING,
        6: constants.SEASON_SUMMER,
        7: constants.SEASON_SUMMER,
        8: constants.SEASON_SUMMER,
        9: constants.SEASON_FALL,
        10: constants.SEASON_FALL,
        11: constants.SEASON_FALL,
    }

    return season_map.get(date.month) if date else None


# Function to check captcha
async def check_cloudflare_captcha(response, secret):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={"response": response, "secret": secret},
            ) as result:
                data = await result.json()
                return data["success"]

    except aiohttp.ClientConnectorError:
        return False
