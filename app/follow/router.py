from tortoise.fields.relational import ManyToManyRelation
from app.utils import pagination_dict, pagination
from fastapi import APIRouter, Depends
from app.dependencies import get_page
from app.models import User
from typing import Tuple
from app import display
from . import service

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
router = APIRouter(prefix="/follow")


@router.get("/{username}", response_model=FollowResponse)
async def check(users: Tuple[User, User] = Depends(validate_self)):
    return {"follow": await service.is_following(*users)}


@router.put("/{username}", response_model=FollowResponse)
async def follow(users: Tuple[User, User] = Depends(validate_follow)):
    return {"follow": await service.follow(*users)}


@router.delete("/{username}", response_model=FollowResponse)
async def unfollow(users: Tuple[User, User] = Depends(validate_unfollow)):
    return {"follow": await service.unfollow(*users)}


@router.get("/{username}/stats", response_model=FollowStatsResponse)
async def follow_stats(user: User = Depends(validate_username)):
    return await service.get_follow_stats(user)


@router.get("/{username}/{action}", response_model=UserPaginationResponse)
async def follow_list(
    relation: ManyToManyRelation = Depends(validate_action),
    page: int = Depends(get_page),
):
    # Pagination
    total = await relation.filter().count()
    limit, offset, size = pagination(page)

    result = await relation.filter().limit(limit).offset(offset)

    return {
        "list": [display.user(follow_user) for follow_user in result],
        "pagination": pagination_dict(total, page, size),
    }
