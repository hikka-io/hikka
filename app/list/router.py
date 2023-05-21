from app.utils import pagination, pagination_dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_user, get_page
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User
from . import service

from .schemas import (
    AnimeFavouritePaginationResponse,
    WatchPaginationResponse,
    WatchFilterArgs,
)


router = APIRouter(prefix="/list", tags=["List"])


@router.get("/{username}/anime", response_model=WatchPaginationResponse)
async def anime_list(
    session: AsyncSession = Depends(get_session),
    args: WatchFilterArgs = Depends(),
    user: User = Depends(get_user),
    page: int = Depends(get_page),
):
    limit, offset = pagination(page)
    total = await service.get_user_watch_count(session, user, args.status)
    result = await service.get_user_watch(
        session, user, args.status, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": [watch for watch in result],
    }


@router.get(
    "/{username}/anime/favourite",
    response_model=AnimeFavouritePaginationResponse,
)
async def anime_favourite_list(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user),
    page: int = Depends(get_page),
):
    limit, offset = pagination(page)
    total = await service.get_user_anime_favourite_count(session, user)
    result = await service.get_user_anime_favourite(
        session, user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": [favourite for favourite in result],
    }
