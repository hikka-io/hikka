from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import SuccessResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import Comment, User
from app.utils import path_to_uuid
from .utils import build_comments
from app import constants
from . import service

from .dependencies import (
    validate_comment_not_hidden,
    validate_comment_edit,
    validate_content_slug,
    validate_rate_limit,
    validate_parent,
    validate_comment,
    validate_hide,
)

from app.utils import (
    pagination_dict,
    pagination,
)

from app.dependencies import (
    auth_required,
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


@router.get("/latest", response_model=list[CommentResponse])
@router.get("/latest/new", response_model=list[CommentResponse])
async def latest_comments(session: AsyncSession = Depends(get_session)):
    comments = await service.latest_comments(session)
    return [
        CommentNode.create(path_to_uuid(comment.reference), comment)
        for comment in comments
    ]


@router.get("/list", response_model=CommentListResponse)
@router.get("/list/new", response_model=CommentListResponse)
async def comments_list(
    request_user: User = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_COMMENT_SCORE])
    ),
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.count_comments(session)
    comments = await service.get_comments(session, request_user, limit, offset)

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": [
            CommentNode.create(path_to_uuid(comment.reference), comment)
            for comment in comments
        ],
    }


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

    comment = await service.generate_preview(session, comment)

    return CommentNode.create(path_to_uuid(comment.reference), comment)


@router.get("/{content_type}/{slug}/list", response_model=CommentListResponse)
async def get_contents_list(
    session: AsyncSession = Depends(get_session),
    content_id: str = Depends(validate_content_slug),
    request_user: User = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_COMMENT_SCORE])
    ),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.count_comments_by_content_id(session, content_id)
    base_comments = await service.get_comments_by_content_id(
        session, content_id, request_user, limit, offset
    )

    result = []

    for base_comment in base_comments:
        sub_comments = await service.get_sub_comments(
            session, base_comment, request_user
        )

        result.append(build_comments(base_comment, sub_comments))

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": result,
    }


@router.put("/{comment_reference}", response_model=CommentResponse)
async def edit_comment(
    args: CommentTextArgs,
    session: AsyncSession = Depends(get_session),
    comment: Comment = Depends(validate_comment_edit),
):
    comment = await service.edit_comment(session, comment, args.text)
    comment = await service.generate_preview(session, comment)
    return CommentNode.create(path_to_uuid(comment.reference), comment)


@router.delete("/{comment_reference}", response_model=SuccessResponse)
async def hide_comment(
    session: AsyncSession = Depends(get_session),
    comment: Comment = Depends(validate_comment),
    user: User = Depends(validate_hide),
):
    comment = await service.hide_comment(session, comment, user)
    return {"success": True}


@router.get("/thread/{comment_reference}", response_model=CommentResponse)
async def thread(
    base_comment: Comment = Depends(validate_comment_not_hidden),
    request_user: User = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_COMMENT_SCORE])
    ),
    session: AsyncSession = Depends(get_session),
):
    sub_comments = await service.get_sub_comments(
        session, base_comment, request_user
    )

    return build_comments(base_comment, sub_comments)
