from app.dependencies import get_user, get_page
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Anime, AnimeWatch
from app.schemas import SuccessResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from typing import Tuple
from . import service

from app.utils import (
    pagination_dict,
    pagination,
)

from .schemas import (
    WatchPaginationResponse,
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
):
    limit, offset = pagination(page)
    total = await service.get_user_watch_list_count(session, user, args.status)
    anime = await service.get_user_watch_list(
        session, user, args.status, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": anime.all(),
    }
