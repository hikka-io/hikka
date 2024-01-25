from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import validate_content_slug
from fastapi import APIRouter, Depends
from app.database import get_session
from .utils import build_comments
from app.models import User
from app import constants
from . import service

from app.utils import (
    pagination_dict,
    pagination,
)

from app.dependencies import (
    auth_required,
    check_captcha,
    get_page,
    get_size,
)

from .schemas import (
    CommentListResponse,
    CommentResponse,
    ContentTypeEnum,
    CommentNode,
    CommentArgs,
)


router = APIRouter(prefix="/comment", tags=["Comments"])


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


@router.get("/{content_type}/{slug}/list", response_model=CommentListResponse)
async def get_content_edit_list(
    session: AsyncSession = Depends(get_session),
    content_id: str = Depends(validate_content_slug),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.count_comments_by_content_id(session, content_id)
    base_comments = await service.get_comments_by_content_id(
        session, content_id, limit, offset
    )

    result = []

    for base_comment in base_comments:
        sub_comments = await service.get_sub_comments(session, base_comment)
        result.append(build_comments(base_comment, sub_comments))

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": result,
    }
