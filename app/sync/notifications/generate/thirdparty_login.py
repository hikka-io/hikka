from sqlalchemy.ext.asyncio import AsyncSession

from app import constants
from app.client.service import get_client
from app.models import Log
from app.models.system.notification import Notification
from app.utils import utcnow


async def generate_thirdparty_login(session: AsyncSession, log: Log):
    notification_type = constants.NOTIFICATION_THIRDPARTY_LOGIN

    client = await get_client(session, log.target_id)

    notification = Notification(
        **{
            "notification_type": notification_type,
            "log_id": log.id,
            "seen": False,
            "user_id": log.user_id,
            "created": log.created,
            "updated": log.created,
            "data": {
                "client": {
                    "name": client.name,
                    "description": client.description,
                    "reference": client.reference,
                },
                "scope": log.data["scope"],
            },
        }
    )

    session.add(notification)
