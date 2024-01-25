from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import validate_content_slug
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import Comment, User
from sqlalchemy import select, func
from .utils import build_comments
from app import constants
from . import service

from app.dependencies import (
    auth_required,
    check_captcha,
    get_page,
    get_size,
)

from .schemas import (
    CommentResponse,
    ContentTypeEnum,
    CommentNode,
    CommentArgs,
)

router = APIRouter(prefix="/comments")


@router.put(
    "/{content_type}/{slug}",
    response_model=CommentResponse,
)
async def write_comment(
    args: CommentArgs,
    content_type: ContentTypeEnum,
    session: AsyncSession = Depends(get_session),
    content_id: str = Depends(validate_content_slug),
    author: User = Depends(
        auth_required(permissions=[constants.PERMISSION_WRITE_COMMENT])
    ),
    _: bool = Depends(check_captcha),
):
    comment = await service.create_comment(
        session, content_type, content_id, author, args.text
    )

    return CommentNode(
        comment.reference,
        comment.text,
        comment.author,
    )


# @router.get("/test", response_model=list[CommentResponse])
# async def test_comments(session: AsyncSession = Depends(get_session)):
#     result = []

#     base_comments = await session.scalars(
#         select(Comment).filter(func.nlevel(Comment.path) == 1)
#     )

#     for base_comment in base_comments:
#         sub_comments = await session.scalars(
#             select(Comment).filter(
#                 Comment.path.descendant_of(base_comment.path),
#                 Comment.id != base_comment.id,
#             )
#         )

#         result.append(build_comments(base_comment, sub_comments))

#     return result
