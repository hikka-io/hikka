from app.models import Review, Anime, Manga, Novel, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists


async def has_review(
    session: AsyncSession,
    user: User,
    content: Anime | Manga | Novel,
    content_type: str,
):
    return await session.scalar(
        select(
            exists().where(
                Review.content_type == content_type,
                Review.content_id == content.id,
                Review.user == user,
            )
        )
    )
