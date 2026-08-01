from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Comment, Review, User
from sqlalchemy import select, exists, func
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


async def get_review_stats(
    session: AsyncSession,
    content_type: str,
    content_id: UUID,
) -> dict:
    """Count reviews grouped by recommendation for given content"""

    # Hidden comments keep their review row around until it's deleted
    # so we join comments here to not count them
    result = await session.execute(
        select(Review.recommended, func.count(Review.id))
        .join(Comment, Review.comment_id == Comment.id)
        .filter(
            Review.content_type == content_type,
            Review.content_id == content_id,
            Comment.hidden == False,  # noqa: E712
            Comment.deleted == False,  # noqa: E712
        )
        .group_by(Review.recommended)
    )

    # Keys here match ReviewRecommended literal
    stats = {"yes": 0, "no": 0, "maybe": 0}

    for recommended, count in result:
        stats[recommended] = count

    return stats
