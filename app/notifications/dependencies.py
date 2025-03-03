from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from app.database import get_session
from app.models import Anime
from app.errors import Abort
from app.models import User
from fastapi import Depends
from uuid import UUID
from . import service


async def validate_notification(
    notification_reference: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(auth_required()),
) -> Anime:
    if not (
        notification := await service.get_notification(
            session, notification_reference, user
        )
    ):
        raise Abort("notification", "not-found")

    return notification
