from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User
from app import constants
from . import service


from .schemas import (
    HistoryPaginationResponse,
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


router = APIRouter(prefix="/history", tags=["History"])


@router.get(
    "/following",
    response_model=HistoryPaginationResponse,
    summary="Following history",
)
async def following_history(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(
            scope=[constants.SCOPE_READ_HISTORY, constants.SCOPE_READ_FOLLOW]
        )
    ),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    user_ids = await service.following_ids(session, user)

    limit, offset = pagination(page, size)
    total = await service.get_following_history_count(session, user_ids)
    history = await service.get_following_history(
        session, user_ids, limit, offset
    )
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": history.all(),
    }


@router.get(
    "/user/{username}",
    response_model=HistoryPaginationResponse,
    summary="User history",
)
async def user_history(
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
