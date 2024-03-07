from app.dependencies import get_anime, auth_required
from app.models import Anime, User, AnimeFavourite
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.errors import Abort
from fastapi import Depends
from . import service


async def validate_get_favourite(
    content_type: str,
    session: AsyncSession = Depends(get_session),
    anime: Anime = Depends(get_anime),
    user: User = Depends(auth_required()),
) -> AnimeFavourite:
    if not (favourite := await service.get_favourite(session, anime, user)):
        raise Abort("favourite", "not-found")

    return favourite


async def validate_add_favourite(
    content_type: str,
    session: AsyncSession = Depends(get_session),
    anime: Anime = Depends(get_anime),
    user: User = Depends(auth_required()),
) -> Anime:
    if await service.get_favourite(session, anime, user):
        raise Abort("favourite", "exists")

    return anime
