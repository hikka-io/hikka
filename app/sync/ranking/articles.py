from sqlalchemy import select, delete, desc, func
from app.models import Article, UserArticleStats
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import sessionmanager
from datetime import timedelta
from app.utils import utcnow
from app import constants


async def recalculate_article_stats(session: AsyncSession):
    print("Recalculating top article author stats")

    articles_count_weight = 1.5
    comment_count_weight = 1
    vote_weight = 2

    last_30_days = utcnow() - timedelta(days=30)

    result = await session.execute(
        select(
            Article.author_id,
            func.count(Article.id).label("total_articles"),
            func.sum(Article.vote_score).label("total_likes"),
            func.sum(Article.comments_count).label("total_comments"),
            (
                (func.sum(Article.vote_score) * vote_weight)
                + (func.sum(Article.comments_count) * comment_count_weight)
                + (func.count(Article.id) * articles_count_weight)
            ).label("author_score"),
        )
        .filter(
            Article.created >= last_30_days,
            Article.category.not_in([constants.ARTICLE_SYSTEM]),
            Article.deleted == False,  # noqa: E712
            Article.draft == False,  # noqa: E712
        )
        .group_by(Article.author_id)
        .order_by(desc("author_score"))
        .limit(10)  # Remove this if we want to calculate ranking for all users
    )

    stats_list = result.fetchall()
    user_ids = [stats.author_id for stats in stats_list]

    # Before movign forward we delete all outdated records
    await session.execute(
        delete(UserArticleStats).filter(
            UserArticleStats.user_id.not_in(user_ids)
        )
    )

    user_stats_list = await session.scalars(
        select(UserArticleStats).filter(UserArticleStats.user_id.in_(user_ids))
    )

    user_stats_cache = {
        user_stats.user_id: user_stats for user_stats in user_stats_list
    }

    for stats in stats_list:
        if not (user_stats := user_stats_cache.get(stats.author_id)):
            user_stats = UserArticleStats(
                **{
                    "user_id": stats.author_id,
                    "total_articles": 0,
                    "total_comments": 0,
                    "author_score": 0,
                    "total_likes": 0,
                }
            )

            session.add(user_stats)

        user_stats.total_articles = stats.total_articles
        user_stats.total_comments = stats.total_comments
        user_stats.author_score = stats.author_score
        user_stats.total_likes = stats.total_likes

    await session.commit()


async def update_article_stats():
    """Recalculare article stats"""

    async with sessionmanager.session() as session:
        await recalculate_article_stats(session)
