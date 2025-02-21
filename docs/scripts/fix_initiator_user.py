from app.models import Notification, User
from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select
from app import constants
import asyncio


async def fix_initiator_user():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        notifications = await session.scalars(
            select(Notification).filter(
                Notification.initiator_user == None,
                Notification.notification_type.in_(
                    [
                        constants.NOTIFICATION_COMMENT_REPLY,
                        constants.NOTIFICATION_COMMENT_VOTE,
                        constants.NOTIFICATION_COMMENT_TAG,
                        constants.NOTIFICATION_COLLECTION_COMMENT,
                        constants.NOTIFICATION_COLLECTION_VOTE,
                        constants.NOTIFICATION_EDIT_COMMENT,
                        constants.NOTIFICATION_EDIT_ACCEPTED,
                        constants.NOTIFICATION_EDIT_DENIED,
                        constants.NOTIFICATION_EDIT_UPDATED,
                        constants.NOTIFICATION_FOLLOW,
                    ]
                ),
            )
        )

        users_cache = {}

        for notification in notifications:
            username = notification.data["username"]

            if username not in users_cache:
                if not (
                    user := await session.scalar(
                        select(User).filter(User.username == username)
                    )
                ):
                    print(f"Failed to find user with username {username}")
                    continue

                users_cache[username] = user

            notification.initiator_user = users_cache[username]

            print(
                f"Added initiator user {username} for notification {notification.id}"
            )

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_initiator_user())
