from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import Comment, User
from .utils import build_comments
from .utils import path_to_uuid
from . import service

from .dependencies import (
    validate_comment_edit,
    validate_content_slug,
    validate_rate_limit,
    validate_parent,
)

from app.utils import (
    pagination_dict,
    pagination,
)

from app.dependencies import (
    get_page,
    get_size,
)

from .schemas import (
    CommentListResponse,
    CommentResponse,
    ContentTypeEnum,
    CommentTextArgs,
    CommentNode,
    CommentArgs,
)


router = APIRouter(prefix="/comments", tags=["Comments"])


@router.put("/{content_type}/{slug}", response_model=CommentResponse)
async def write_comment(
    args: CommentArgs,
    content_type: ContentTypeEnum,
    session: AsyncSession = Depends(get_session),
    content_id: str = Depends(validate_content_slug),
    parent: Comment | None = Depends(validate_parent),
    author: User = Depends(validate_rate_limit),
):
    comment = await service.create_comment(
        session, content_type, content_id, author, args.text, parent
    )

    return CommentNode.create(path_to_uuid(comment.reference), comment)


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


@router.put("/{comment_reference}", response_model=CommentResponse)
async def update_comment(
    args: CommentTextArgs,
    session: AsyncSession = Depends(get_session),
    comment: Comment = Depends(validate_comment_edit),
):
    comment = await service.update_comment(session, comment, args.text)
    return CommentNode.create(path_to_uuid(comment.reference), comment)
