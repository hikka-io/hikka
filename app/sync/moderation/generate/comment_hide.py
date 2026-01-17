from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Moderation, Log
from app import constants
from .. import service


async def generate_comment_hide(session: AsyncSession, log: Log):
    target_type = constants.MODERATION_COMMENT_HIDDEN

    if not (comment := await service.get_comment(session, log.target_id)):
        return

    if not comment:
        return

    if comment.author_id == comment.hidden_by_id:
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
                "content_type": comment.content_type,
                "content_slug": comment.preview["slug"],
                "comment_path": comment.path,
            },
        }
    )

    session.add(moderation)
