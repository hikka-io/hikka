from datetime import datetime, timedelta
from .service import get_user_by_auth
from fastapi import Header, Query
from .errors import Abort
from .models import User


# Get current pagination page
async def get_page(page: int = Query(gt=0, default=1)):
    return page


# Check user auth token
async def auth_required(auth: str = Header()) -> User:
    if not (token := await get_user_by_auth(auth)):
        raise Abort("auth", "invalid-token")

    if not token.user:
        raise Abort("auth", "user-not-found")

    if token.user.banned:
        raise Abort("auth", "banned")

    now = datetime.utcnow()

    if now > token.expiration:
        raise Abort("auth", "token-expired")

    token.expiration = now + timedelta(days=3)
    await token.save()

    return token.user
