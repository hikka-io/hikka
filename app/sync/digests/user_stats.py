from app.models import SystemTimestamp, Edit, Comment, Digest, Log
from sqlalchemy.dialects.postgresql import insert
from app.database import sessionmanager
from app.utils import utcnow, chunkify
from sqlalchemy import select, func
from datetime import datetime
from app import constants


async def generate_user_stats(session):
    now = utcnow()

    if not (
        system_timestamp := await session.scalar(
            select(SystemTimestamp).filter(SystemTimestamp.name == "user_stats")
        )
    ):
        system_timestamp = SystemTimestamp(
            **{
                "timestamp": datetime(2024, 1, 13),
                "name": "user_stats",
            }
        )

    # Get new logs that were created since last update
    logs = await session.execute(
        select(Log.user_id, func.max(Log.created).label("latest"))
        .filter(
            Log.log_type.in_(
                [
                    constants.LOG_COMMENT_WRITE,
                    constants.LOG_COMMENT_HIDE,
                    constants.LOG_EDIT_CREATE,
                ]
            )
        )
        .filter(
            Log.created > system_timestamp.timestamp,
            Log.user_id != None,  # noqa: E711
        )
        .group_by(Log.user_id)
    )

    max_time = None
    result = {}

    for log in logs:
        if max_time is None:
            max_time = log.latest

        max_time = max(max_time, log.latest)

        edits_count = await session.scalar(
            select(func.count(Edit.id).filter(Edit.author_id == log.user_id))
        )

        comments_count = await session.scalar(
            select(
                func.count(Comment.id).filter(
                    Comment.author_id == log.user_id,
                    Comment.deleted == False,  # noqa: E712
                    Comment.hidden == False,  # noqa: E712
                )
            )
        )

        result[log.user_id] = {
            "comments_count": comments_count,
            "edits_count": edits_count,
        }

    values = [
        {
            "name": constants.DIGEST_USER_STATS,
            "user_id": user_id,
            "created": now,
            "updated": now,
            "data": data,
        }
        for user_id, data in result.items()
    ]

    for values_chunk in chunkify(values, 100):
        await session.execute(
            insert(Digest)
            .values(values_chunk)
            .on_conflict_do_update(
                index_elements=["user_id", "name"],
                set_={
                    "updated": insert(Digest).excluded.updated,
                    "data": insert(Digest).excluded.data,
                },
            )
        )

    system_timestamp.timestamp = max_time

    print(f"Updated user stats digests for {len(result)} users")

    await session.commit()


async def digest_user_stats():
    async with sessionmanager.session() as session:
        await generate_user_stats(session)
