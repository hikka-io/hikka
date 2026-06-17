from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Comment, Review, User
from sqlalchemy import select, exists
from uuid import UUID


async def has_review(
    session: AsyncSession,
    user: User,
    content_id: UUID,
    content_type: str,
    exclude_comment: Comment | None = None,
):
    exists_query = exists().where(
        Review.content_type == content_type,
        Review.content_id == content_id,
        Review.user == user,
    )

    if exclude_comment is not None:
        exists_query = exists_query.where(Review.comment != exclude_comment)

    return await session.scalar(select(exists_query))
