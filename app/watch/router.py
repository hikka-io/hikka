from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Anime, AnimeWatch
from app.schemas import SuccessResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from app import constants
from typing import Tuple
from . import service

from app.dependencies import (
    get_user,
    get_page,
    get_size,
)

from app.utils import (
    pagination_dict,
    pagination,
)

from .schemas import (
    WatchPaginationResponse,
    WatchStatsResponse,
    WatchFilterArgs,
    WatchResponse,
    WatchArgs,
)

from .dependencies import (
    verify_add_watch,
    verify_watch,
)


router = APIRouter(prefix="/watch", tags=["Watch"])


@router.get("/{slug}", response_model=WatchResponse)
async def watch_get(watch: AnimeWatch = Depends(verify_watch)):
    return watch


@router.put("/{slug}", response_model=WatchResponse)
async def watch_add(
    data: Tuple[Anime, User, WatchArgs] = Depends(verify_add_watch),
    session: AsyncSession = Depends(get_session),
):
    return await service.save_watch(session, *data)


@router.delete("/{slug}", response_model=SuccessResponse)
async def delete_watch(
    watch: AnimeWatch = Depends(verify_watch),
    session: AsyncSession = Depends(get_session),
):
    await service.delete_watch(session, watch)
    return {"success": True}


@router.get("/{username}/list", response_model=WatchPaginationResponse)
async def user_watch_list(
    session: AsyncSession = Depends(get_session),
    args: WatchFilterArgs = Depends(),
    user: User = Depends(get_user),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_user_watch_list_count(session, user, args.status)
    anime = await service.get_user_watch_list(
        session, user, args.status, args.order, args.sort, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": anime.all(),
    }


@router.get(
    "/{username}/stats",
    summary="Get user watch list stats",
    response_model=WatchStatsResponse,
)
async def user_watch_stats(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user),
):
    # This looks awful -> refactor it into something better
    completed = await service.get_user_watch_stats(
        session, user, constants.WATCH_COMPLETED
    )

    watching = await service.get_user_watch_stats(
        session, user, constants.WATCH_WATCHING
    )

    planned = await service.get_user_watch_stats(
        session, user, constants.WATCH_PLANNED
    )

    on_hold = await service.get_user_watch_stats(
        session, user, constants.WATCH_ON_HOLD
    )

    dropped = await service.get_user_watch_stats(
        session, user, constants.WATCH_DROPPED
    )

    return {
        "completed": completed,
        "watching": watching,
        "planned": planned,
        "on_hold": on_hold,
        "dropped": dropped,
    }
