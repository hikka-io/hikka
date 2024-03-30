from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Notification, Log
from app import constants
from .. import service


async def generate_anime_schedule(session: AsyncSession, log: Log):
    notification_type = constants.NOTIFICATION_SCHEDULE_ANIME

    # Just in case anime missing for some odd reason
    if not (anime := await service.get_anime(session, log.target_id)):
        return

    user_ids = await service.get_anime_watch_user_ids(session, anime)

    # ToDo: batch check for existing notifications here

    for user_id in user_ids:
        # Do not create notification if we already did that
        if await service.get_notification(
            session, user_id, log.id, notification_type
        ):
            continue

        notification = Notification(
            **{
                "notification_type": notification_type,
                "created": log.created,
                "updated": log.created,
                "user_id": user_id,
                "log_id": log.id,
                "seen": False,
                "data": {
                    "slug": anime.slug,
                    "poster": anime.poster,
                    "title_ja": anime.title_ja,
                    "title_en": anime.title_en,
                    "title_ua": anime.title_ua,
                    "before": log.data["before"],
                    "after": log.data["after"],
                },
            }
        )

        session.add(notification)
