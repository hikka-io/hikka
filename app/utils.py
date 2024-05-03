from dateutil.relativedelta import relativedelta
from datetime import datetime, UTC
from functools import lru_cache
from urllib.parse import quote
from dynaconf import Dynaconf
from datetime import timezone
from app.models import User
from app import constants
from uuid import UUID
import unicodedata
import aiohttp
import secrets
import bcrypt
import math
import re


# Replacement for deprecated datetime's utcnow
def utcnow():
    return datetime.now(UTC).replace(tzinfo=None)


# Replacement for deprecated datetime's utcfromtimestamp
def utcfromtimestamp(timestamp: int):
    return datetime.fromtimestamp(timestamp, UTC).replace(tzinfo=None)


# Simple check for permissions
# TODO: move to separate file with role logic
def check_user_permissions(user: User, permissions: list):
    role_permissions = constants.ROLES.get(user.role, [])

    has_permission = all(
        permission in role_permissions for permission in permissions
    )

    return has_permission


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
        (
            transliterate[letter.lower()]
            if letter.lower() in transliterate
            else letter
        )
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
    return utcfromtimestamp(timestamp) if timestamp else None


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
    # Anime seasons start from first month of the year
    season_map = {
        1: constants.SEASON_WINTER,
        2: constants.SEASON_WINTER,
        3: constants.SEASON_WINTER,
        4: constants.SEASON_SPRING,
        5: constants.SEASON_SPRING,
        6: constants.SEASON_SPRING,
        7: constants.SEASON_SUMMER,
        8: constants.SEASON_SUMMER,
        9: constants.SEASON_SUMMER,
        10: constants.SEASON_FALL,
        11: constants.SEASON_FALL,
        12: constants.SEASON_FALL,
    }

    return season_map.get(date.month) if date else None


# Get datetime for next month since provided datetime
def get_next_month(date):
    return date.replace(day=1) + relativedelta(months=1)


# I hate overly discriptive function names
def days_until_next_month(date):
    return (get_next_month(date) - date).days


# Get list of seasons anime aired in for provided range of dates
def get_airing_seasons(start_date: datetime, end_date: datetime | None):
    end_date = utcnow() if not end_date else end_date

    airing_seasons = []
    date = start_date

    if days_until_next_month(date) < 7:
        date = get_next_month(date)

    while date <= end_date:
        season = [get_season(date), date.year]

        if season not in airing_seasons:
            airing_seasons.append(season)

        date = get_next_month(date)

    return [f"{entry[0]}_{entry[1]}" for entry in airing_seasons]


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


def is_protected_username(username: str):
    usernames = [
        ["admin", "blog", "dev", "ftp", "mail", "pop", "pop3", "imap", "smtp"],
        ["stage", "stats", "status", "www", "beta", "about", "access"],
        ["account", "accounts", "add", "address", "adm"],
        ["administration", "adult", "advertising", "affiliate", "affiliates"],
        ["ajax", "analytics", "android", "anon", "anonymous", "api"],
        ["app", "apps", "archive", "atom", "auth", "authentication"],
        ["avatar", "backup", "banner", "banners", "bin", "billing", "blog"],
        ["blogs", "board", "bot", "bots", "business", "chat"],
        ["cache", "cadastro", "calendar", "campaign", "careers"],
        ["cgi", "client", "cliente", "code", "comercial", "compare", "config"],
        ["connect", "contact", "contest", "create", "code", "compras"],
        ["css", "dashboard", "data", "db", "design", "delete"],
        ["demo", "design", "designer", "dev", "devel", "dir"],
        ["directory", "doc", "docs", "domain", "download", "downloads"],
        ["edit", "editor", "email", "ecommerce", "forum", "forums"],
        ["faq", "favorite", "feed", "feedback", "flog", "follow"],
        ["file", "files", "free", "ftp", "gadget", "gadgets"],
        ["games", "guest", "group", "groups", "help", "home", "homepage"],
        ["host", "hosting", "hostname", "html", "http", "httpd"],
        ["https", "hpg", "info", "information", "image", "img", "images"],
        ["imap", "index", "invite", "intranet", "indice", "ipad", "iphone"],
        ["irc", "java", "javascript", "job", "jobs", "js"],
        ["knowledgebase", "log", "login", "logs", "logout", "list", "lists"],
        ["mail", "mail1", "mail2", "mail3", "mail4", "mail5"],
        ["mailer", "mailing", "mx", "manager", "marketing"],
        ["master", "me", "media", "message", "microblog", "microblogs"],
        ["mine", "mp3", "msg", "msn", "mysql", "messenger"],
        ["mob", "mobile", "movie", "movies", "music", "musicas"],
        ["my", "name", "named", "net", "network", "new"],
        ["news", "newsletter", "nick", "nickname", "notes", "noticias"],
        ["ns", "ns1", "ns2", "ns3", "ns4", "ns5", "ns6", "ns7", "ns8"],
        ["ns9", "ns10", "old", "online", "operator", "order", "orders"],
        ["page", "pager", "pages", "panel", "password", "perl", "pic", "pics"],
        ["photo", "photos", "photoalbum", "php", "plugin", "plugins", "pop"],
        ["pop3", "post", "postmaster", "postfix", "posts"],
        ["profile", "project", "projects", "promo", "pub", "public", "python"],
        ["random", "register", "registration", "root", "ruby", "rss"],
        ["sale", "sales", "sample", "samples", "script", "scripts", "secure"],
        ["send", "service", "shop", "sql", "signup", "signin", "search"],
        ["security", "settings", "setting", "setup", "site"],
        ["sites", "sitemap", "smtp", "soporte", "ssh", "stage", "staging"],
        ["start", "subscribe", "subdomain", "suporte", "support", "stat"],
        ["static", "stats", "status", "store", "stores", "system"],
        ["tablet", "tablets", "tech", "telnet", "test", "test1", "test2"],
        ["test3", "teste", "tests", "theme", "themes", "tmp"],
        ["todo", "task", "tasks", "tools", "tv", "talk", "update", "upload"],
        ["url", "user", "username", "usuario", "usage", "vendas"],
        ["video", "videos", "visitor", "win", "ww", "www"],
        ["www1", "www2", "www3", "www4", "www5", "www6", "www7"],
        ["wwww", "wws", "wwws", "web", "webmail", "website", "websites"],
        ["webmaster", "workshop", "xxx", "xpg", "you"],
        ["hikka"],
    ]

    usernames = list(set(item for sublist in usernames for item in sublist))

    return username in usernames


def is_empty_markdown(text):
    # First we remove markdown tags
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # **text**
    text = re.sub(r"\*(.*?)\*", r"\1", text)  # *text*
    text = re.sub(r"__(.*?)__", r"\1", text)  # __text__
    text = re.sub(r"\[.*?\]\((.*?)\)", r"\1", text)  # [text](link)
    text = re.sub(r":::spoiler(.*?):::", r"\1", text)  # :::spoiler content :::

    # Then remove spaces
    text = text.replace(" ", "")

    # And now check if string is empty
    return len(text) == 0


# I really hate this
def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def is_uuid(string):
    try:
        UUID(string)
        return True
    except ValueError:
        return False


# Convert comment path to uuid reference
def path_to_uuid(obj_uuid):
    return str(obj_uuid).replace("_", "-")


# Collection ranking algorithm
def calculate_collection_ranking(score, favourite, comments, created):
    def boost_factor(day, boost_factor=10.0, boost_duration_days=30):
        decay_rate = -math.log(1 / boost_factor) / boost_duration_days
        return max(boost_factor * math.exp(-decay_rate * day), 1)

    boost_duration_days = 30
    now = utcnow()

    weight_score = 1
    weight_favourite = 2
    weight_comment = 0.1

    ranking = 0
    ranking += weight_score * score
    ranking += weight_favourite * favourite
    ranking += weight_comment * comments

    days_since_creation = (now - created).days
    ranking *= boost_factor(days_since_creation, boost_duration_days)

    return round(ranking, 8)
