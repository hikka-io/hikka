from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Comment, Edit
from app.errors import Abort
from fastapi import Depends
from . import service

from .schemas import (
    ContentTypeEnum,
    CommentArgs,
)


async def validate_content(
    slug: str,
    content_type: ContentTypeEnum,
    session: AsyncSession = Depends(get_session),
) -> Edit:
    if not (
        content := await service.get_content_by_slug(
            session, content_type, slug
        )
    ):
        raise Abort("comment", "content-not-found")

    return content


async def validate_content_slug(
    content: Edit = Depends(validate_content),
) -> str:
    return content.reference


async def validate_parent(
    args: CommentArgs,
    content_type: ContentTypeEnum,
    content_id: Edit = Depends(validate_content_slug),
    session: AsyncSession = Depends(get_session),
) -> Comment | None:
    if not args.parent:
        return None

    if not (
        parent_comment := await service.get_comment(
            session, content_type, content_id, args.parent
        )
    ):
        raise Abort("comment", "parent-not-found")

    max_reply_depth = 3
    if len(parent_comment.path) > max_reply_depth:
        raise Abort("comment", "max-depth")

    return parent_comment
