from app.utils import path_to_uuid, paginated_response, pagination
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import SuccessResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import Comment, User
from .utils import build_comments
from app import constants
from . import service

from .dependencies import (
    validate_comment_not_hidden,
    validate_comment_edit,
    validate_comment_get,
    validate_rate_limit,
    validate_comment,
    validate_content,
    validate_parent,
    validate_hide,
)

from app.dependencies import (
    auth_required,
    get_page,
    get_size,
)

from .schemas import (
    CommentableType,
    CommentListResponse,
    CommentResponse,
    ContentTypeEnum,
    CommentTextArgs,
    CommentNode,
    CommentArgs,
)


router = APIRouter(prefix="/comments", tags=["Comments"])


@router.get("/latest", response_model=list[CommentResponse])
async def latest_comments(session: AsyncSession = Depends(get_session)):
    comments = await service.latest_comments(session)
    return [
        CommentNode.create(path_to_uuid(comment.reference), comment)
        for comment in comments
    ]


@router.get("/list", response_model=CommentListResponse)
async def comments_list(
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
    request_user: User = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_COMMENT_SCORE])
    ),
):
    limit, offset = pagination(page, size)
    total = await service.count_comments(session)
    comments = await service.get_comments(session, request_user, limit, offset)

    return paginated_response(
        [
            CommentNode.create(path_to_uuid(comment.reference), comment)
            for comment in comments
        ],
        total,
        page,
        limit,
    )


@router.put("/{content_type}/{slug}", response_model=CommentResponse)
async def write_comment(
    args: CommentArgs,
    content_type: ContentTypeEnum,
    session: AsyncSession = Depends(get_session),
    parent: Comment | None = Depends(validate_parent),
    author: User = Depends(validate_rate_limit),
    content: CommentableType = Depends(validate_content),
):
    comment = await service.create_comment(
        session, content_type, content, author, args.text, parent
    )

    comment = await service.generate_preview(session, comment)

    return CommentNode.create(path_to_uuid(comment.reference), comment)


@router.get("/{content_type}/{slug}/list", response_model=CommentListResponse)
async def get_contents_list(
    session: AsyncSession = Depends(get_session),
    content: CommentableType = Depends(validate_content),
    request_user: User = Depends(
        auth_required(optional=True, scope=[constants.SCOPE_READ_COMMENT_SCORE])
    ),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    total = content.comments_count_pagination
    limit, offset = pagination(page, size)
    base_comments = await service.get_comments_by_content_id(
        session, content.id, request_user, limit, offset
    )

    result = []

    for base_comment in base_comments:
        sub_comments = await service.get_sub_comments(
            session, base_comment, request_user
        )

        result.append(build_comments(base_comment, sub_comments))

    return paginated_response(result, total, page, limit)


@router.get("/{comment_reference}", response_model=CommentResponse)
async def get_comment(
    session: AsyncSession = Depends(get_session),
    comment: Comment = Depends(validate_comment_get),
    user: User = Depends(auth_required(optional=True)),
):
    comment = await service.get_comment(session, comment.id, user)

    sub_comments = await service.get_sub_comments(session, comment, user)

    comment = await service.generate_preview(session, comment)
    return build_comments(comment, sub_comments)


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
    await service.hide_comment(session, comment, user)
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
