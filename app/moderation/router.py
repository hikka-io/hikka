from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from . import service


from .schemas import (
    ModerationPaginationResponse,
)

from app.utils import (
    pagination_dict,
    pagination,
)

from app.dependencies import (
    get_page,
    get_size,
)


router = APIRouter(prefix="/moderation", tags=["Moderation"])


@router.get(
    "/history",
    response_model=ModerationPaginationResponse,
    summary="Moderation history",
)
async def moderation_history(
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_moderation_count(session)
    history = await service.get_moderation(session, limit, offset)

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": history.all(),
    }
