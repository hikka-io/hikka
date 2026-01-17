from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import validate_notification
from app.models import Notification, User
from fastapi import APIRouter, Depends
from app.database import get_session
from app import constants
from . import service

from .schemas import (
    NotificationPaginationResponse,
    NotificationUnseenResponse,
    NotificationResponse,
)

from app.utils import (
    paginated_response,
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
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_READ_NOTIFICATION])
    ),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.get_user_notifications_count(session, user)
    notifications = await service.get_user_notifications(
        session, user, limit, offset
    )

    return paginated_response(notifications.all(), total, page, limit)


@router.get(
    "/count",
    response_model=NotificationUnseenResponse,
    summary="Unseen notifications count",
)
async def unseen_notifications_count(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(scope=[constants.SCOPE_READ_NOTIFICATION])
    ),
):
    return {"unseen": await service.get_unseen_count(session, user)}


@router.post(
    "/{notification_reference}/seen",
    response_model=NotificationResponse,
    summary="Mark notification as seen",
    dependencies=[
        Depends(auth_required(scope=[constants.SCOPE_SEEN_NOTIFICATION])),
    ],
)
async def notification_seen(
    notification: Notification = Depends(validate_notification),
    session: AsyncSession = Depends(get_session),
):
    await service.notification_seen(session, notification)
    return notification
