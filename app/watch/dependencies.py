from app.dependencies import get_anime, auth_required
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AnimeWatch, Anime, User
from app.database import get_session
from .schemas import WatchArgs
from app.errors import Abort
from fastapi import Depends
from typing import Tuple
from . import service


async def verify_watch(
    anime: Anime = Depends(get_anime),
    user: User = Depends(auth_required()),
    session: AsyncSession = Depends(get_session),
) -> AnimeWatch:
    if not (watch := await service.get_anime_watch(session, anime, user)):
        raise Abort("watch", "not-found")

    return watch


async def verify_add_watch(
    args: WatchArgs,
    anime: Anime = Depends(get_anime),
    user: User = Depends(auth_required()),
) -> Tuple[Anime, User, WatchArgs]:
    # User can't set more than 0 episodes if anime not yet aired
    if not anime.episodes and args.episodes > 0:
        raise Abort("watch", "bad-episodes")

    # Make sure user provided episodes within constraints
    if anime.episodes and args.episodes > anime.episodes:
        raise Abort("watch", "bad-episodes")

    return anime, user, args
