from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Moderation, Log
from app import constants
from .. import service


async def generate_edit_update(session: AsyncSession, log: Log):
    target_type = constants.MODERATION_EDIT_UPDATED

    if not (edit := await service.get_edit(session, log.target_id)):
        return

    if not edit.author:
        return

    if edit.author_id == log.user_id:
        return

    if await service.get_moderation(
        session,
        log.user_id,
        log.id,
        target_type,
    ):
        return

    await session.refresh(log, attribute_names=["user"])

    moderation = Moderation(
        **{
            "target_type": target_type,
            "user_id": log.user_id,
            "created": log.created,
            "log_id": log.id,
            "data": {
                "updated_edit": log.data["updated_edit"],
                "old_edit": log.data["old_edit"],
                "username": log.user.username,
                "avatar": log.user.avatar,
                "edit_id": edit.edit_id,
            },
        }
    )

    session.add(moderation)
