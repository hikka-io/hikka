from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Moderation, Log
from app import constants
from .. import service


async def generate_collection_update(session: AsyncSession, log: Log):
    target_type = constants.MODERATION_COLLECTION_UPDATED

    if not (collection := await service.get_collection(session, log.target_id)):
        return

    if not collection.author:
        return

    if collection.author_id == log.user_id:
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
                "updated_collection": log.data["updated_collection"],
                "old_collection": log.data["old_collection"],
                "username": log.user.username,
                "avatar": log.user.avatar,
                "collection_id": str(collection.id),
            },
        }
    )

    session.add(moderation)
