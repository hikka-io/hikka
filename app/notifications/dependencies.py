from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from app.database import get_session
from . import service, grouping
from app.models import Anime
from app.errors import Abort
from app.models import User
from fastapi import Depends
from datetime import date
from uuid import UUID


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


async def validate_notification_group(
    group_reference: str,
) -> tuple[str, str, date]:
    if not (parsed := grouping.parse_group_reference(group_reference)):
        raise Abort("notification", "not-found")

    notification_type, subkey, day = parsed

    try:
        return notification_type, subkey, date.fromisoformat(day)
    except ValueError:
        raise Abort("notification", "not-found")
