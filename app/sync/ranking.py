from app.utils import calculate_collection_ranking
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc, func
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from datetime import datetime
from app import constants

from app.models import (
    CollectionFavourite,
    CollectionComment,
    SystemTimestamp,
    Collection,
    Log,
)


async def collection_stats(session: AsyncSession, collection: Collection):
    favourite = await session.scalar(
        select(func.count(CollectionFavourite.id)).filter(
            CollectionFavourite.content_id == collection.id,
        )
    )

    comments = await session.scalar(
        select(func.count(CollectionComment.id)).filter(
            CollectionComment.content_id == collection.id,
            CollectionComment.hidden == False,  # noqa: E712
        )
    )

    return favourite, comments, collection.vote_score


async def recalculate_ranking_daily(session: AsyncSession):
    collections = await session.scalars(select(Collection))

    for collection in collections:
        favourite, comments, score = await collection_stats(session, collection)

        collection.system_ranking = calculate_collection_ranking(
            score, favourite, comments, collection.created
        )

        print(
            f"Updated collection {collection.title} ranking to {collection.system_ranking}"
        )

        session.add(collection)

    await session.commit()


async def recalculate_ranking(session: AsyncSession):
    # Get system timestamp for latest ranking update
    if not (
        system_timestamp := await session.scalar(
            select(SystemTimestamp).filter(SystemTimestamp.name == "ranking")
        )
    ):
        system_timestamp = SystemTimestamp(
            **{
                "timestamp": datetime(2024, 1, 13),
                "name": "ranking",
            }
        )

    # Get new logs that were created since last update
    logs = await session.scalars(
        select(Log)
        .filter(
            Log.log_type.in_(
                [
                    constants.LOG_FAVOURITE,
                    constants.LOG_FAVOURITE_REMOVE,
                    constants.LOG_COMMENT_WRITE,
                    constants.LOG_COMMENT_HIDE,
                    constants.LOG_VOTE_SET,
                ]
            )
        )
        .filter(Log.created > system_timestamp.timestamp)
        .order_by(asc(Log.created))
    )

    for log in logs:
        # We set timestamp here because after thay it won't be set due to continue
        system_timestamp.timestamp = log.created

        collection = None

        if log.log_type in [
            constants.LOG_FAVOURITE,
            constants.LOG_FAVOURITE_REMOVE,
            constants.LOG_VOTE_SET,
        ]:
            if log.data["content_type"] != constants.CONTENT_COLLECTION:
                continue

            collection = await session.scalar(
                select(Collection).filter(Collection.id == log.target_id)
            )

        if log.log_type in [
            constants.LOG_COMMENT_WRITE,
            constants.LOG_COMMENT_HIDE,
        ]:
            if log.data["content_type"] != constants.CONTENT_COLLECTION:
                continue

            comment = await session.scalar(
                select(CollectionComment)
                .filter(CollectionComment.id == log.target_id)
                .options(selectinload(CollectionComment.content))
            )

            collection = comment.content

        if collection:
            favourite, comments, score = await collection_stats(
                session, collection
            )

            collection.system_ranking = calculate_collection_ranking(
                score, favourite, comments, collection.created
            )

            # print(
            #     f"Updated collection {collection.title} ranking to {collection.system_ranking} ({log.log_type})"
            # )

            session.add(collection)

    session.add(system_timestamp)
    await session.commit()


async def update_ranking():
    """Recalculare user generateg content ranking from logs"""

    async with sessionmanager.session() as session:
        await recalculate_ranking(session)


async def update_ranking_daily():
    """Recalculare user generateg content ranking from logs daily"""

    async with sessionmanager.session() as session:
        await recalculate_ranking_daily(session)
