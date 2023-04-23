from pydantic.datetime_parse import parse_datetime
import bcrypt

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
