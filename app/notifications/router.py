from .schemas import NotificationPaginationResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import User
from . import service


from app.utils import (
    pagination_dict,
    pagination,
)

from app.dependencies import (
    auth_required,
    get_page,
    get_size,
)


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "",
    response_model=NotificationPaginationResponse,
    summary="Notifications",
)
async def notifications(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(auth_required()),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_user_notifications_count(session, user)
    notifications = await service.get_user_notifications(
        session, user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": notifications.all(),
    }
