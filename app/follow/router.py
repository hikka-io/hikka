from app.utils import pagination_dict, pagination
from fastapi import APIRouter, Depends
from app.dependencies import get_page
from app.models import User
from typing import Tuple
from . import service

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session

from .dependencies import (
    validate_username,
    validate_unfollow,
    validate_follow,
    validate_action,
    validate_self,
)

from .schemas import (
    UserPaginationResponse,
    FollowStatsResponse,
    FollowResponse,
)


# ToDo: Better responses
router = APIRouter(prefix="/follow", tags=["Follow"])


@router.get("/{username}", response_model=FollowResponse)
async def check(
    users: Tuple[User, User] = Depends(validate_self),
    session: AsyncSession = Depends(get_session),
):
    return {"follow": await service.is_following(session, *users)}


@router.put("/{username}", response_model=FollowResponse)
async def follow(
    users: Tuple[User, User] = Depends(validate_follow),
    session: AsyncSession = Depends(get_session),
):
    return {"follow": await service.follow(session, *users)}


@router.delete("/{username}", response_model=FollowResponse)
async def unfollow(
    users: Tuple[User, User] = Depends(validate_unfollow),
    session: AsyncSession = Depends(get_session),
):
    return {"follow": await service.unfollow(session, *users)}


@router.get("/{username}/stats", response_model=FollowStatsResponse)
async def follow_stats(
    user: User = Depends(validate_username),
    session: AsyncSession = Depends(get_session),
):
    return {
        "followers": await service.count_followers(session, user),
        "following": await service.count_following(session, user),
    }


@router.get("/{username}/{action}", response_model=UserPaginationResponse)
async def follow_list(
    session: AsyncSession = Depends(get_session),
    action: str = Depends(validate_action),
    user: User = Depends(validate_username),
    page: int = Depends(get_page),
):
    if action == "following":
        count_function, list_function = (
            service.count_following,
            service.list_following,
        )

    if action == "followers":
        count_function, list_function = (
            service.count_followers,
            service.list_followers,
        )

    total = await count_function(session, user)
    limit, offset = pagination(page)
    result = await list_function(session, user, limit, offset)

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": [follow_user for follow_user in result],
    }
