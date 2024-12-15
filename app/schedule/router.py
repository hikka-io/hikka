from .schemas import AnimeScheduleResponsePaginationResponse
from .dependencies import validate_schedule_args
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import AnimeScheduleArgs
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User
from app import constants
from . import service

from app.dependencies import (
    auth_required,
    get_page,
    get_size,
)

from app.utils import (
    paginated_response,
    pagination,
)


router = APIRouter(prefix="/schedule", tags=["Schedule"])


@router.post("/anime", response_model=AnimeScheduleResponsePaginationResponse)
async def anime_schedule(
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_WATCHLIST])
    ),
    args: AnimeScheduleArgs = Depends(validate_schedule_args),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_schedule_anime_count(session, args, request_user)
    schedule = await service.get_schedule_anime(
        session, args, request_user, limit, offset
    )

    return paginated_response(schedule.unique().all(), total, page, limit)
