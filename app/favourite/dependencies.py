from app.dependencies import get_anime, auth_required
from app.models import Anime, User, AnimeFavourite
from app.errors import Abort
from fastapi import Depends
from typing import Tuple
from . import service


async def get_anime_and_user(
    anime: Anime = Depends(get_anime), user: User = Depends(auth_required)
) -> Tuple[Anime, User]:
    return anime, user


async def get_anime_favourite(
    data: Tuple[Anime, User] = Depends(get_anime_and_user)
) -> AnimeFavourite:
    if not (favourite := await service.get_anime_favourite(*data)):
        raise Abort("favourite", "not-found")

    return favourite


async def add_anime_favourite(
    data: Tuple[Anime, User] = Depends(get_anime_and_user)
) -> Tuple[Anime, User]:
    if await service.get_anime_favourite(*data):
        raise Abort("favourite", "exists")

    return data
