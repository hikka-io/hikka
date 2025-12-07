from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app import meilisearch
from app.models import User
from app import constants
from . import service

from .schemas import (
    UserWithEmailResponse,
    UserResponseFollowed,
    ActivityResponse,
)

from app.schemas import (
    QuerySearchRequiredArgs,
    UserResponse,
)

from app.dependencies import (
    auth_required,
    get_user,
)

from .dependencies import (
    get_user_followed_reference,
    get_user_followed_username,
)


router = APIRouter(prefix="/user", tags=["User"])


@router.get(
    "/me",
    response_model=UserWithEmailResponse,
    summary="Current user profile",
)
async def profile(
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_READ_USER_DETAILS])
    ),
):
    return user


@router.get(
    "/{reference:uuid}",
    response_model=UserResponseFollowed,
    summary="User profile by id",
)
async def user_profile_by_id(user: User = Depends(get_user_followed_reference)):
    return user


@router.get(
    "/{username}",
    response_model=UserResponseFollowed,
    summary="User profile",
)
async def user_profile_by_username(
    user: User = Depends(get_user_followed_username),
):
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
