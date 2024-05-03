from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from .schemas import ActivityResponse
from app.database import get_session
from app import meilisearch
from app.models import User
from app import constants
from . import service

from app.schemas import (
    QuerySearchArgs,
    UserResponse,
)

from app.history.schemas import HistoryPaginationResponse  # TODO: remove me!
from app.history.service import get_user_history_count  # TODO: remove me!
from app.history.service import get_user_history  # TODO: remove me!

from app.utils import (
    pagination_dict,
    pagination,
)

from app.dependencies import (
    auth_required,
    get_user,
    get_page,
    get_size,
)


router = APIRouter(prefix="/user", tags=["User"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Current user profile",
)
async def profile(user: User = Depends(auth_required())):
    return user


@router.get(
    "/{username}",
    response_model=UserResponse,
    summary="User profile",
)
async def user_profile(user: User = Depends(get_user)):
    return user


# TODO: remove me!
@router.get(
    "/{username}/history",
    response_model=HistoryPaginationResponse,
    summary="User history",
)
async def service_user_history(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await get_user_history_count(session, user)
    history = await get_user_history(session, user, limit, offset)
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": history.all(),
    }


@router.get(
    "/{username}/activity",
    response_model=list[ActivityResponse],
    summary="User activity",
)
async def service_user_activity(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user),
):
    activity = await service.get_user_activity(session, user)
    return activity.all()[::-1]


@router.post("/list", response_model=list[UserResponse])
async def search_users(
    args: QuerySearchArgs, session: AsyncSession = Depends(get_session)
):
    meilisearch_result = await meilisearch.search(
        constants.SEARCH_INDEX_USERS, query=args.query
    )

    return await service.users_meilisearch(session, meilisearch_result)
