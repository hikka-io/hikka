from .schemas import AnimeScheduleResponsePaginationResponse
from .dependencies import validate_schedule_args
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import AnimeScheduleArgs
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User
from . import service

from app.dependencies import (
    auth_required,
    get_page,
    get_size,
)

from app.utils import (
    pagination_dict,
    pagination,
)


router = APIRouter(prefix="/schedule", tags=["Schedule"])


@router.post("/anime", response_model=AnimeScheduleResponsePaginationResponse)
async def anime_schedule(
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(auth_required(optional=True)),
    args: AnimeScheduleArgs = Depends(validate_schedule_args),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_schedule_anime_count(session, args)
    schedule = await service.get_schedule_anime(
        session, args, request_user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": schedule.unique().all(),
    }
