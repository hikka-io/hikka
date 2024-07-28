from sqlalchemy.ext.asyncio import AsyncSession
from app.service import get_content_by_slug
from app.dependencies import auth_required
from app.models import Comment, Edit, User
from app.database import get_session
from app.errors import Abort
from fastapi import Depends
from app import constants
from uuid import UUID
from app import utils
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
    if not (content := await get_content_by_slug(session, content_type, slug)):
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
        parent_comment := await service.get_comment_by_content(
            session, content_type, content_id, args.parent
        )
    ):
        raise Abort("comment", "parent-not-found")

    max_reply_depth = 5
    if len(parent_comment.path) >= max_reply_depth:
        raise Abort("comment", "max-depth")

    return parent_comment


async def validate_rate_limit(
    session: AsyncSession = Depends(get_session),
    author: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_COMMENT_WRITE],
            scope=[constants.SCOPE_CREATE_COMMENT],
        )
    ),
):
    comments_limit = 100
    comments_total = await service.count_comments_limit(session, author)

    if comments_total >= comments_limit:
        raise Abort("comment", "rate-limit")

    return author


async def validate_comment(
    comment_reference: UUID,
    session: AsyncSession = Depends(get_session),
    request_user: User = Depends(auth_required(optional=True)),
) -> Comment:
    if not (
        comment := await service.get_comment(
            session, comment_reference, request_user
        )
    ):
        raise Abort("comment", "not-found")

    return comment


async def validate_comment_not_hidden(
    comment: Comment = Depends(validate_comment),
):
    if comment.hidden:
        raise Abort("comment", "hidden")

    return comment


async def validate_comment_edit(
    comment: Comment = Depends(validate_comment_not_hidden),
    author: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_COMMENT_EDIT],
            scope=[constants.SCOPE_UPDATE_COMMENT],
        )
    ),
):
    if comment.author != author:
        raise Abort("comment", "not-owner")

    if not comment.is_editable:
        raise Abort("comment", "not-editable")

    return comment


async def validate_hide(
    comment: Comment = Depends(validate_comment),
    user: User = Depends(auth_required(scope=constants.SCOPE_DELETE_COMMENT)),
):
    if comment.hidden:
        raise Abort("comment", "already-hidden")

    # User either trying to hide own comment (PERMISSION_COMMENT_HIDE)
    # Or it is admin hiding somebody's else comment (PERMISSION_COMMENT_HIDE_ADMIN)
    permission = (
        constants.PERMISSION_COMMENT_HIDE
        if comment.author == user
        else constants.PERMISSION_COMMENT_HIDE_ADMIN
    )

    if not utils.check_user_permissions(user, [permission]):
        raise Abort("permission", "denied")

    return user
