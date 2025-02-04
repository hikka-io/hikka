from sqlalchemy.ext.asyncio import AsyncSession
from app.models import UserArticleStats, User
from sqlalchemy import select


async def get_or_create_user_article_stats(session: AsyncSession, user: User):
    if not (
        stats := await session.scalar(
            select(UserArticleStats).filter(UserArticleStats.user == user)
        )
    ):
        stats = UserArticleStats(**{"user": user})
        session.add(stats)

    return stats
