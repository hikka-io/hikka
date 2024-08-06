from app.utils import pagination_dict, pagination
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User
from app import constants
from typing import Tuple
from . import service

from app.dependencies import (
    auth_required,
    get_page,
    get_size,
)

from .dependencies import (
    validate_username,
    validate_unfollow,
    validate_follow,
    validate_self,
)

from .schemas import (
    FollowUserPaginationResponse,
    FollowStatsResponse,
    FollowResponse,
)


router = APIRouter(prefix="/follow", tags=["Follow"])


@router.get(
    "/{username}",
    response_model=FollowResponse,
    summary="Check follow",
    dependencies=[
        Depends(auth_required(scope=[constants.SCOPE_READ_FAVOURITE]))
    ],
)
async def check(
    session: AsyncSession = Depends(get_session),
    users: Tuple[User, User] = Depends(validate_self),
):
    return {"follow": await service.is_following(session, *users)}


@router.put(
    "/{username}",
    response_model=FollowResponse,
    summary="Follow",
    dependencies=[Depends(auth_required(scope=[constants.SCOPE_FOLLOW]))],
)
async def follow(
    session: AsyncSession = Depends(get_session),
    users: Tuple[User, User] = Depends(validate_follow),
):
    return {"follow": await service.follow(session, *users)}


@router.delete(
    "/{username}",
    response_model=FollowResponse,
    summary="Unfollow",
    dependencies=[Depends(auth_required(scope=[constants.SCOPE_UNFOLLOW]))],
)
async def unfollow(
    session: AsyncSession = Depends(get_session),
    users: Tuple[User, User] = Depends(validate_unfollow),
):
    return {"follow": await service.unfollow(session, *users)}


@router.get(
    "/{username}/stats",
    response_model=FollowStatsResponse,
    summary="Follow stats",
)
async def follow_stats(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(validate_username),
):
    return {
        "followers": await service.count_followers(session, user),
        "following": await service.count_following(session, user),
    }


@router.get(
    "/{username}/following",
    response_model=FollowUserPaginationResponse,
    summary="Followed users",
)
async def following_list(
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_FOLLOW])
    ),
    user: User = Depends(validate_username),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.count_following(session, user)
    following = await service.list_following(
        session, request_user, user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": following.all(),
    }


@router.get(
    "/{username}/followers",
    response_model=FollowUserPaginationResponse,
    summary="Followers",
)
async def followers_list(
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_FOLLOW])
    ),
    user: User = Depends(validate_username),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.count_followers(session, user)
    followers = await service.list_followers(
        session, request_user, user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": followers.all(),
    }
