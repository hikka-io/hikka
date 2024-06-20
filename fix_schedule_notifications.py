from app.database import sessionmanager
from app.models import Notification
from app.utils import get_settings
from sqlalchemy import select
from app import constants
import asyncio
import copy


async def fix_schedule_notifications():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        notifications = await session.scalars(
            select(Notification).filter(
                Notification.notification_type
                == constants.NOTIFICATION_SCHEDULE_ANIME
            )
        )

        for notification in notifications:
            if "image" in notification.data:
                continue

            notification.data = copy.deepcopy(notification.data)

            notification.data["image"] = notification.data["poster"]

            session.add(notification)
            await session.commit()

            print(f"Fixed notification {notification.id}")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_schedule_notifications())
