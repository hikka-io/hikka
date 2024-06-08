from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from .schemas import ActivityResponse
from app.database import get_session
from app import meilisearch
from app.models import User
from app import constants
from . import service

from app.schemas import (
    QuerySearchRequiredArgs,
    UserResponse,
)

from app.dependencies import (
    auth_required,
    get_user,
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
    args: QuerySearchRequiredArgs, session: AsyncSession = Depends(get_session)
):
    meilisearch_result = await meilisearch.search(
        constants.SEARCH_INDEX_USERS, query=args.query
    )

    return await service.users_meilisearch(session, meilisearch_result)
