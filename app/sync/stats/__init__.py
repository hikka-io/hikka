from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc, func
from app.database import sessionmanager
from sqlalchemy.orm import joinedload
from datetime import datetime
from app import constants
from . import service

from app.models import (
    SystemTimestamp,
    Article,
    Log,
)


async def generate_stats(session: AsyncSession):
    # Get system timestamp for latest history update
    if not (
        system_timestamp := await session.scalar(
            select(SystemTimestamp).filter(SystemTimestamp.name == "stats")
        )
    ):
        system_timestamp = SystemTimestamp(
            **{
                "timestamp": datetime(2024, 1, 13),
                "name": "stats",
            }
        )

    # Get new logs that were created since last update
    logs = await session.scalars(
        select(Log)
        .filter(
            Log.log_type.in_(
                [
                    constants.LOG_ARTICLE_CREATE,
                    constants.LOG_ARTICLE_DELETE,
                ]
            )
        )
        .filter(Log.created > system_timestamp.timestamp)
        .order_by(asc(Log.created))
    )

    for log in logs:
        # We set timestamp here because after thay it won't be set due to continue
        system_timestamp.timestamp = log.created

        if log.log_type in [
            constants.LOG_ARTICLE_CREATE,
            constants.LOG_ARTICLE_DELETE,
        ]:
            if not (
                article := await session.scalar(
                    select(Article)
                    .options(joinedload(Article.author))
                    .filter(Article.id == log.target_id)
                )
            ):
                continue

            stats = await service.get_or_create_user_article_stats(
                session, article.author
            )

            # TODO: This is horrybly inefficient and we should fix it one day
            for category in [constants.ARTICLE_REVIEWS, constants.ARTICLE_NEWS]:
                articles_count = await session.scalar(
                    select(func.count(Article.id)).filter(
                        Article.category == category,
                        Article.deleted == False,  # noqa: E712
                        Article.draft == False,  # noqa: E712
                    )
                )

                setattr(stats, category, articles_count)

    session.add(system_timestamp)
    await session.commit()


async def update_stats():
    """Generate users stats from logs"""

    async with sessionmanager.session() as session:
        await generate_stats(session)
