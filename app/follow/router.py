from app.utils import pagination_dict, pagination
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_page, get_size
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User
from typing import Tuple
from . import service

from .dependencies import (
    validate_username,
    validate_unfollow,
    validate_follow,
    validate_self,
)

from .schemas import (
    UserPaginationResponse,
    FollowStatsResponse,
    FollowResponse,
)


router = APIRouter(prefix="/follow", tags=["Follow"])


@router.get(
    "/{username}",
    response_model=FollowResponse,
    summary="Check follow",
)
async def check(
    users: Tuple[User, User] = Depends(validate_self),
    session: AsyncSession = Depends(get_session),
):
    return {"follow": await service.is_following(session, *users)}


@router.put(
    "/{username}",
    response_model=FollowResponse,
    summary="Follow",
)
async def follow(
    users: Tuple[User, User] = Depends(validate_follow),
    session: AsyncSession = Depends(get_session),
):
    return {"follow": await service.follow(session, *users)}


@router.delete(
    "/{username}",
    response_model=FollowResponse,
    summary="Unfollow",
)
async def unfollow(
    users: Tuple[User, User] = Depends(validate_unfollow),
    session: AsyncSession = Depends(get_session),
):
    return {"follow": await service.unfollow(session, *users)}


@router.get(
    "/{username}/stats",
    response_model=FollowStatsResponse,
    summary="Follow stats",
)
async def follow_stats(
    user: User = Depends(validate_username),
    session: AsyncSession = Depends(get_session),
):
    return {
        "followers": await service.count_followers(session, user),
        "following": await service.count_following(session, user),
    }


@router.get(
    "/{username}/following",
    response_model=UserPaginationResponse,
    summary="Followed users",
)
async def following_list(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(validate_username),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.count_following(session, user)
    following = await service.list_following(session, user, limit, offset)
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": following.all(),
    }


@router.get(
    "/{username}/followers",
    response_model=UserPaginationResponse,
    summary="Followers",
)
async def followers_list(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(validate_username),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.count_followers(session, user)
    followers = await service.list_followers(session, user, limit, offset)
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": followers.all(),
    }
