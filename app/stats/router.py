from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import EditsTopPaginationResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from . import service

from app.dependencies import (
    get_page,
    get_size,
)

from app.utils import (
    pagination_dict,
    pagination,
)


router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/edits/top", response_model=EditsTopPaginationResponse)
async def edits_top(
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_edits_top_count(session)
    top = await service.get_edits_top(session, limit, offset)

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": top.all(),
    }
