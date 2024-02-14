from app.schemas import SuccessResponse, AnimeResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Anime, AnimeWatch
from app.dependencies import auth_required
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
    AnimeWatchSearchArgs,
    WatchStatsResponse,
    WatchStatusEnum,
    WatchFilterArgs,
    WatchResponse,
    WatchArgs,
)

from .dependencies import (
    verify_user_random,
    verify_add_watch,
    verify_watch,
)


router = APIRouter(prefix="/watch", tags=["Watch"])


@router.get("/{slug}", response_model=WatchResponse)
async def watch_get(watch: AnimeWatch = Depends(verify_watch)):
    return watch


@router.put("/{slug}", response_model=WatchResponse)
async def watch_add(
    session: AsyncSession = Depends(get_session),
    data: Tuple[Anime, User, WatchArgs] = Depends(verify_add_watch),
):
    return await service.save_watch(session, *data)


@router.delete("/{slug}", response_model=SuccessResponse)
async def delete_watch(
    session: AsyncSession = Depends(get_session),
    watch: AnimeWatch = Depends(verify_watch),
    user: User = Depends(auth_required()),
):
    await service.delete_watch(session, watch, user)
    return {"success": True}


@router.get("/{username}/list", response_model=WatchPaginationResponse)
async def user_watch_list_legacy(
    session: AsyncSession = Depends(get_session),
    args: WatchFilterArgs = Depends(),
    user: User = Depends(get_user),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_user_watch_list_count_legacy(
        session, user, args.status
    )
    anime = await service.get_user_watch_list_legacy(
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

    duration = await service.get_user_watch_duration(session, user)

    return {
        "duration": duration,
        "completed": completed,
        "watching": watching,
        "planned": planned,
        "on_hold": on_hold,
        "dropped": dropped,
    }


@router.get("/random/{username}/{status}", response_model=AnimeResponse)
async def random_watch_entry(
    status: WatchStatusEnum,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(verify_user_random),
):
    result = await service.random_watch(session, user, status)
    return result


@router.post(
    "/{username}/list",
    response_model=WatchPaginationResponse,
)
async def user_watch_list(
    search: AnimeWatchSearchArgs,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_user_watch_list_count(session, search, user)
    anime = await service.get_user_watch_list(
        session, search, user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": anime.all(),
    }
