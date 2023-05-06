from datetime import datetime, timedelta
from .service import get_auth_token
from fastapi import Header, Query
from .errors import Abort
from .models import User


# Get current pagination page
async def get_page(page: int = Query(gt=0, default=1)):
    return page


# Check user auth token
async def auth_required(auth: str = Header()) -> User:
    if not (token := await get_auth_token(auth)):
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

    token.user.last_active = now
    await token.user.save()

    return token.user
