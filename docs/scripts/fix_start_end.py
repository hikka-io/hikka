from app.models import AnimeWatch, Read
from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select
from app.models import Log
from app import constants
import asyncio


async def update_start_end(
    session,
    status_create,
    status_update,
    status_delete,
    model,
    model_content_id,
):
    logs = await session.scalars(
        select(Log)
        .filter(
            Log.log_type.in_(
                [
                    status_create,
                    status_update,
                    status_delete,
                ]
            )
        )
        .order_by(Log.created.asc())
    )

    cache = {}

    for log in logs:
        key = (log.user_id, log.target_id)

        if key not in cache:
            cache[key] = {"start": log.created, "end": None}

        if log.log_type in [
            status_create,
            status_update,
        ]:
            if (
                "after" in log.data
                and "status" in log.data["after"]
                and log.data["after"]["status"] == status_create
                and cache[key]["end"] is None
            ):
                cache[key]["end"] = log.created

        if log.log_type == status_delete:
            cache.pop(key)

    for key in cache:
        user_id, content_id = key

        entry = await session.scalar(
            select(model).filter(
                model.user_id == user_id,
                model_content_id == content_id,
            )
        )

        if not entry or (
            entry.start_date is not None and entry.end_date is not None
        ):
            continue

        if entry.start_date is None:
            entry.start_data = cache[key]["start"]

        if entry.end_date is None:
            entry.end_data = cache[key]["end"]

    await session.commit()


async def fix_start_end():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        print("Fixing watch records")
        await update_start_end(
            session,
            constants.LOG_WATCH_CREATE,
            constants.LOG_WATCH_UPDATE,
            constants.LOG_WATCH_DELETE,
            AnimeWatch,
            AnimeWatch.anime_id,
        )

        print("Fixing read records")
        await update_start_end(
            session,
            constants.LOG_READ_CREATE,
            constants.LOG_READ_UPDATE,
            constants.LOG_READ_DELETE,
            Read,
            Read.content_id,
        )

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_start_end())
