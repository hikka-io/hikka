from pydantic.datetime_parse import parse_datetime
from unicodedata import normalize
from datetime import datetime
import bcrypt
import re

# Get bcrypt hash of password
def hashpwd(password: str) -> str:
    return bcrypt.hashpw(
        str.encode(password), bcrypt.gensalt()
    ).decode()

# Check bcrypt password hash
def checkpwd(password: str, bcrypt_hash: str) -> bool:
    return bcrypt.checkpw(
        str.encode(password), str.encode(bcrypt_hash)
    )

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

def from_timestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp) if timestamp else None

def to_timestamp(date):
    return int(date.timestamp()) if date else None
