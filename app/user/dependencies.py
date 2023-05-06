from app.errors import Abort
from app.models import User


async def get_profile(username: str) -> User:
    if not (user := await User.filter(username=username).first()):
        raise Abort("user", "not-found")

    return user
