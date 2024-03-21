from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import ContentTypeEnum
from sqlalchemy import select, func
from app.service import create_log
from datetime import datetime
from app import constants

from app.models import (
    CollectionVote,
    CommentVote,
    Collection,
    Comment,
    User,
    Vote,
)


content_type_to_favourite_class = {
    constants.CONTENT_COLLECTION: CollectionVote,
    constants.CONTENT_COMMENT: CommentVote,
}


async def get_vote(
    session: AsyncSession,
    content_type: ContentTypeEnum,
    content: Collection | Comment,
    user: User,
) -> Vote | None:
    vote_model = content_type_to_favourite_class[content_type]
    return await session.scalar(
        select(vote_model).filter(
            vote_model.content_id == content.id,
            vote_model.user == user,
        )
    )


async def set_vote(
    session: AsyncSession,
    content_type: ContentTypeEnum,
    content: Collection | Comment,
    user: User,
    user_score: int,
) -> CommentVote:
    vote_model = content_type_to_favourite_class[content_type]
    now = datetime.utcnow()

    # Create watch record if missing
    if not (vote := await get_vote(session, content_type, content, user)):
        vote = vote_model(
            **{
                "content": content,
                "created": now,
                "user": user,
            }
        )

    vote.updated = now
    vote.score = user_score

    session.add(vote)

    if hasattr(content, "score"):
        old_score = content.score
        content.score = await session.scalar(
            select(func.sum(vote_model.score)).filter(
                vote_model.content == content
            )
        )
        new_score = content.score

        session.add(content)
        await session.commit()

        await create_log(
            session,
            constants.LOG_VOTE_SET,
            user,
            content.id,
            {
                "content_type": content_type,
                "user_score": user_score,
                "old_score": old_score,
                "new_score": new_score,
            },
        )

    return vote
