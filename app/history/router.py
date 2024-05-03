from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User
from . import service


from .schemas import (
    HistoryPaginationResponse,
)

from app.utils import (
    pagination_dict,
    pagination,
)

from app.dependencies import (
    get_user,
    get_page,
    get_size,
)


router = APIRouter(prefix="/history", tags=["History"])


@router.get(
    "",
    response_model=HistoryPaginationResponse,
    summary="Global history",
)
async def global_history(
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_history_count(session)
    history = await service.get_history(session, limit, offset)
    return {
        "pagination": pagination_dict(total, page, limit),
        "list": history.all(),
    }


@router.get(
    "/{username}",
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
