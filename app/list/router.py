from app.utils import pagination, pagination_dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_user, get_page
from .schemas import WatchPaginationResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User
from . import service


router = APIRouter(prefix="/list", tags=["List"])


@router.get("/{username}/anime", response_model=WatchPaginationResponse)
async def anime_list(
    user: User = Depends(get_user),
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
):
    total = await service.get_user_watch_count(session, user)
    limit, offset = pagination(page)
    result = await service.get_user_watch(session, user, limit, offset)

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": [watch for watch in result],
    }
