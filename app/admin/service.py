from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from app.admin.schemas import UpdateUserBody
from app.models import Notification, User
from app.utils import utcnow
from app import constants


async def create_hikka_update_notification(
    session: AsyncSession,
    update_name: str,
    description: str,
    title: str,
    link: str,
):
    users = await session.scalars(select(User))
    notification_type = constants.NOTIFICATION_HIKKA_UPDATE
    now = utcnow()

    # Get user ids to make sure we don't duplicate system notification
    user_ids = await session.scalars(
        select(Notification.user_id).filter(
            Notification.data.op("->>")("update_name") == update_name
        )
    )

    user_ids = user_ids.all()

    for user in users:
        if user.id in user_ids:
            continue

        notification = Notification(
            **{
                "notification_type": notification_type,
                "user_id": user.id,
                "created": now,
                "updated": now,
                "seen": False,
                "data": {
                    "update_name": update_name,
                    "description": description,
                    "title": title,
                    "link": link,
                },
            }
        )

        session.add(notification)

    await session.commit()


async def delete_hikka_update_notification(
    session: AsyncSession, update_name: str
):
    await session.execute(
        delete(Notification).filter(
            Notification.data.op("->>")("update_name") == update_name
        )
    )

    await session.commit()


async def count_hikka_update_notifications(
    session: AsyncSession, update_name: str
):
    return await session.scalar(
        select(func.count(Notification.id)).filter(
            Notification.data.op("->>")("update_name") == update_name
        )
    )


async def update_user(session: AsyncSession, user: User, body: UpdateUserBody):
    if body.forbid_actions is not None:
        if body.forbid_actions_merge:
            user.forbidden_actions = list(
                set(user.forbidden_actions + body.forbid_actions)
            )
        else:
            user.forbidden_actions = body.forbid_actions

    if body.remove_avatar:
        user.avatar_image_relation.deletion_request = True
        user.avatar_image_relation = None
        user.avatar_image_id = None

    if body.remove_cover:
        user.cover_image_relation.deletion_request = True
        user.cover_image_relation = None
        user.cover_image_id = None

    if body.description:
        user.description = body.description

    if body.remove_description:
        user.description = None

    if body.banned is not None:
        user.banned = body.banned

    await session.commit()

    return user
