from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from .utils import is_int, uuid_to_path
from .schemas import ContentTypeEnum
from sqlalchemy_utils import Ltree
from datetime import datetime
from app import constants
from uuid import uuid4

from app.models import (
    EditComment,
    Comment,
    User,
    Edit,
)


# This part inspited by edit logic
# If we change edit logic we probably change this as well
content_type_to_content_class = {
    constants.CONTENT_SYSTEM_EDIT: Edit,
}

content_type_to_comment_class = {
    constants.CONTENT_SYSTEM_EDIT: EditComment,
}


async def get_content_by_slug(
    session: AsyncSession, content_type: ContentTypeEnum, slug: str
):
    content_model = content_type_to_content_class[content_type]
    query = select(content_model)

    # Special case for edit
    if content_type == constants.CONTENT_SYSTEM_EDIT:
        if not is_int(slug):
            return None

        query = query.filter(content_model.edit_id == int(slug))

    # Everything else is handled here
    else:
        query = query.filter(content_model.slug == slug)

    return await session.scalar(query)


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
            "created": now,
            "updated": now,
            "id": uuid4(),
            "text": text,
        }
    )

    ltree_id = Ltree(uuid_to_path(comment.id))
    comment.path = ltree_id if parent is None else parent.path + ltree_id

    session.add(comment)
    await session.commit()
    # await session.refresh

    return comment


async def count_comments_by_content_id(
    session: AsyncSession, content_id: str
) -> int:
    """Count comments for given content"""

    return await session.scalar(
        select(func.count(Comment.id)).filter(
            func.nlevel(Comment.path) == 1,
            Comment.content_id == content_id,
        )
    )


async def get_comments_by_content_id(
    session: AsyncSession,
    content_id: str,
    limit: int,
    offset: int,
) -> list[Edit]:
    """Return comemnts for given content"""

    return await session.scalars(
        select(Comment)
        .filter(
            func.nlevel(Comment.path) == 1,
            Comment.content_id == content_id,
        )
        .order_by(desc(Comment.created))
        .limit(limit)
        .offset(offset)
    )


async def get_sub_comments(session: AsyncSession, base_comment: Comment):
    return await session.scalars(
        select(Comment).filter(
            Comment.path.descendant_of(base_comment.path),
            Comment.id != base_comment.id,
        )
    )
