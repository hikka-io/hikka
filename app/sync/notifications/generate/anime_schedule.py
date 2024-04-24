from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Notification, Log
from app import constants
from .. import service


async def generate_anime_schedule(session: AsyncSession, log: Log):
    notification_type = constants.NOTIFICATION_SCHEDULE_ANIME

    # Just in case anime missing for some odd reason
    if not (anime := await service.get_anime(session, log.target_id)):
        return

    anime_watch = await service.get_anime_watch(session, anime)

    # ToDo: batch check for existing notifications here

    for watch in anime_watch:
        # Do not create notification if we already did that
        if await service.get_notification(
            session, watch.user_id, log.id, notification_type
        ):
            continue

        # Stop if user wishes to ignore this type of notifications
        if notification_type in watch.user.ignored_notifications:
            continue

        # Special case for planned/on hold entries
        # We only show notification if status of anime has changed
        if watch.status in [constants.WATCH_PLANNED, constants.WATCH_ON_HOLD]:
            if "status" not in log.data["after"]:
                continue

        notification = Notification(
            **{
                "notification_type": notification_type,
                "user_id": watch.user_id,
                "created": log.created,
                "updated": log.created,
                "log_id": log.id,
                "seen": False,
                "data": {
                    "slug": anime.slug,
                    "poster": anime.poster,
                    "title_ja": anime.title_ja,
                    "title_en": anime.title_en,
                    "title_ua": anime.title_ua,
                    "media_type": anime.media_type,
                    "before": log.data["before"],
                    "after": log.data["after"],
                },
            }
        )

        session.add(notification)
