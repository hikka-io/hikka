from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc, func
from .utils import uuid_to_path, round_hour
from sqlalchemy.orm import with_expression
from .schemas import ContentTypeEnum
from sqlalchemy_utils import Ltree
from datetime import datetime
from uuid import UUID, uuid4
from app import constants
from app import utils
import copy

from app.service import (
    get_my_score_subquery,
    create_log,
)

from app.models import (
    CollectionComment,
    AnimeComment,
    EditComment,
    Comment,
    User,
    Edit,
)


content_type_to_comment_class = {
    constants.CONTENT_COLLECTION: CollectionComment,
    constants.CONTENT_SYSTEM_EDIT: EditComment,
    constants.CONTENT_ANIME: AnimeComment,
}


async def get_comment(
    session: AsyncSession, comment_reference: UUID
) -> Comment:
    return await session.scalar(
        select(Comment).filter(Comment.id == comment_reference)
    )


async def create_comment(
    session: AsyncSession,
    content_type: ContentTypeEnum,
    content_id: str,
    author: User,
    text: str,
    parent: Comment | None = None,
):
    comment_model = content_type_to_comment_class[content_type]
    now = datetime.utcnow()

    comment = comment_model(
        **{
            "content_type": content_type,
            "content_id": content_id,
            "author": author,
            "vote_score": 0,
            "created": now,
            "updated": now,
            "id": uuid4(),
            "text": text,
            "score": 0,
        }
    )

    ltree_id = Ltree(uuid_to_path(comment.id))
    comment.path = ltree_id if parent is None else parent.path + ltree_id

    session.add(comment)
    await session.commit()

    await create_log(
        session,
        constants.LOG_COMMENT_WRITE,
        author,
        comment.id,
    )

    return comment


async def get_comment_by_content(
    session: AsyncSession,
    content_type: ContentTypeEnum,
    content_id: str,
    reference: str,
) -> Comment | None:
    return await session.scalar(
        select(Comment).filter(
            Comment.content_type == content_type,
            Comment.content_id == content_id,
            Comment.id == reference,
        )
    )


async def count_comments_by_content_id(
    session: AsyncSession, content_id: str
) -> int:
    """Count comments for given content"""

    return await session.scalar(
        select(func.count(Comment.id)).filter(
            func.nlevel(Comment.path) == 1,
            Comment.content_id == content_id,
            Comment.hidden == False,  # noqa: E712
        )
    )


async def get_comments_by_content_id(
    session: AsyncSession,
    content_id: str,
    request_user: User | None,
    limit: int,
    offset: int,
) -> list[Edit]:
    """Return comemnts for given content"""

    return await session.scalars(
        select(Comment)
        .filter(
            func.nlevel(Comment.path) == 1,
            Comment.content_id == content_id,
            Comment.hidden == False,  # noqa: E712
        )
        .options(
            with_expression(
                Comment.my_score,
                get_my_score_subquery(
                    Comment, constants.CONTENT_COMMENT, request_user
                ),
            )
        )
        .order_by(desc(Comment.created))
        .limit(limit)
        .offset(offset)
    )


async def get_sub_comments(
    session: AsyncSession,
    base_comment: Comment,
    request_user: User | None,
):
    return await session.scalars(
        select(Comment)
        .filter(
            Comment.path.descendant_of(base_comment.path),
            Comment.id != base_comment.id,
        )
        .options(
            with_expression(
                Comment.my_score,
                get_my_score_subquery(
                    Comment, constants.CONTENT_COMMENT, request_user
                ),
            )
        )
        .order_by(asc(Comment.created))
    )


async def count_comments_limit(session: AsyncSession, author: User) -> int:
    return await session.scalar(
        select(func.count(Comment.id)).filter(
            Comment.author == author,
            Comment.created > round_hour(datetime.utcnow()),
        )
    )


async def edit_comment(
    session: AsyncSession,
    comment: Comment,
    text: str,
) -> Comment:
    now = datetime.utcnow()

    old_text = comment.text
    comment.updated = now
    comment.text = text
    new_text = comment.text

    # SQLAlchemy quirks
    comment.history = copy.deepcopy(comment.history)
    comment.history.append(
        {
            "updated": utils.to_timestamp(now),
            "text": old_text,
        }
    )

    session.add(comment)
    await session.commit()

    await create_log(
        session,
        constants.LOG_COMMENT_EDIT,
        comment.author,
        comment.id,
        data={
            "old_text": old_text,
            "new_text": new_text,
        },
    )

    return comment


async def hide_comment(session: AsyncSession, comment: Comment, user: User):
    comment.updated = datetime.utcnow()
    comment.hidden_by = user
    comment.hidden = True

    session.add(comment)
    await session.commit()

    await create_log(
        session,
        constants.LOG_COMMENT_HIDE,
        user,
        comment.id,
    )

    return True
