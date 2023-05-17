from .service import get_auth_token  # , get_anime_by_slug
from datetime import datetime, timedelta
from fastapi import Header, Query
from .errors import Abort
from .models import User  # , Anime

from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_session
from fastapi import Depends


# Get current pagination page
async def get_page(page: int = Query(gt=0, default=1)):
    return page


# # Get anime by slug
# async def get_anime(slug: str) -> Anime:
#     if not (anime := await get_anime_by_slug(slug)):
#         raise Abort("anime", "not-found")

#     return anime


# Check user auth token
async def auth_required(
    auth: str = Header(), session: AsyncSession = Depends(get_session)
) -> User:
    if not (token := await get_auth_token(session, auth)):
        raise Abort("auth", "invalid-token")

    if not token.user:
        raise Abort("auth", "user-not-found")

    if token.user.banned:
        raise Abort("auth", "banned")

    now = datetime.utcnow()

    if now > token.expiration:
        raise Abort("auth", "token-expired")

    token.expiration = now + timedelta(days=3)
    token.user.last_active = now

    session.add(token)
    await session.commit()

    return token.user
