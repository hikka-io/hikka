from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app.schemas import UserResponse
from app.models import User
from . import service

from .schemas import (
    HistoryPaginationResponse,
    ActivityResponse,
)

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
    total = await service.get_user_history_count(session, user)
    history = await service.get_user_history(session, user, limit, offset)
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
