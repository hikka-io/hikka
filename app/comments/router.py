from app.utils import path_to_uuid, paginated_response, pagination
from app.common.schemas.comments import CommentContentTypeEnum
from app.common.schemas.comments import CommentNode
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
    validate_review_create,
    validate_comment_edit,
    validate_review_edit,
    validate_rate_limit,
    validate_comment,
    validate_content,
    validate_parent,
    validate_hide,
)

from app.dependencies import (
    auth_required,
    get_user,
    get_page,
    get_size,
)

from .schemas import (
    UserCommentsFilterArgs,
    CommentListResponse,
    CommentsFilterArgs,
    CommentableType,
    CommentResponse,
    CommentTextArgs,
    CommentArgs,
)


router = APIRouter(prefix="/comments", tags=["Comments"])


# DEPRECATED
@router.get("/{content_type}/{slug}/list", response_model=CommentListResponse)
async def get_comments_list_legacy(
    filters: CommentsFilterArgs = Depends(),
    session: AsyncSession = Depends(get_session),
    content: CommentableType = Depends(validate_content),
    request_user: User = Depends(
        auth_required(
            scope=[constants.SCOPE_READ_COMMENT_SCORE],
            optional=True,
        )
    ),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    # TODO: do we need to implement caching for reviews?
    # total = content.comments_count_pagination

    total = await service.get_comments_count_by_content_id(
        session, content.id, filters.comment_type, filters.recommended
    )

    limit, offset = pagination(page, size)

    base_comments = await service.get_comments_by_content_id(
        session,
        content.id,
        request_user,
        filters.comment_type,
        filters.recommended,
        filters.sort,
        limit,
        offset,
    )

    result = []

    for base_comment in base_comments:
        sub_comments = await service.get_sub_comments(
            session, base_comment, request_user
        )

        result.append(build_comments(base_comment, sub_comments))

    return paginated_response(result, total, page, limit)


@router.post("/{content_type}/{slug}/list", response_model=CommentListResponse)
async def get_comments_list(
    filters: CommentsFilterArgs,
    session: AsyncSession = Depends(get_session),
    content: CommentableType = Depends(validate_content),
    request_user: User = Depends(
        auth_required(
            scope=[constants.SCOPE_READ_COMMENT_SCORE],
            optional=True,
        )
    ),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    total = await service.get_comments_count_by_content_id(
        session, content.id, filters.comment_type, filters.recommended
    )

    limit, offset = pagination(page, size)

    base_comments = await service.get_comments_by_content_id(
        session,
        content.id,
        request_user,
        filters.comment_type,
        filters.recommended,
        filters.sort,
        limit,
        offset,
    )

    result = []

    for base_comment in base_comments:
        sub_comments = await service.get_sub_comments(
            session, base_comment, request_user
        )

        result.append(
            CommentNode.create(
                path_to_uuid(base_comment.reference), base_comment
            )
        )

        result += [
            CommentNode.create(path_to_uuid(comment.reference), comment)
            for comment in sub_comments
        ][:10]  # TODO: Move this to limit after non flat deprecation

    return paginated_response(result, total, page, limit)


@router.post("/user/{username}", response_model=CommentListResponse)
async def get_comments_user(
    filters: UserCommentsFilterArgs,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user),
    request_user: User = Depends(
        auth_required(
            scope=[constants.SCOPE_READ_COMMENT_SCORE],
            optional=True,
        )
    ),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    total = await service.get_comments_count_by_user(
        session,
        user,
        filters.comment_type,
        filters.recommended,
        filters.first_level_only,
    )

    limit, offset = pagination(page, size)

    comments = await service.get_comments_by_user(
        session,
        user,
        request_user,
        filters.comment_type,
        filters.recommended,
        filters.sort,
        limit,
        offset,
        filters.first_level_only,
    )

    result = [
        CommentNode.create(path_to_uuid(comment.reference), comment)
        for comment in comments
    ]

    return paginated_response(result, total, page, limit)


@router.get(
    "/thread/{comment_reference}",
    # NOTE: this is not usual practice to have 2 types of response
    # and we shold remove CommentResponse after non flat comments are deprecated
    response_model=CommentResponse | CommentListResponse,
)
async def thread(
    base_comment: Comment = Depends(validate_comment_not_hidden),
    request_user: User = Depends(
        auth_required(
            scope=[constants.SCOPE_READ_COMMENT_SCORE],
            optional=True,
        )
    ),
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
    flat: bool = False,
):
    # TODO: same as above this exists only for backward compatibility
    # and should be removed in the future
    if not flat:
        sub_comments = await service.get_sub_comments(
            session, base_comment, request_user
        )

        return build_comments(base_comment, sub_comments)

    else:
        result = []

        total = await service.get_comments_count_by_thread(
            session, base_comment
        )

        limit, offset = pagination(page, size)

        comments = await service.get_comments_by_thread(
            session,
            base_comment,
            request_user,
            limit,
            offset,
        )

        result = [
            CommentNode.create(path_to_uuid(comment.reference), comment)
            for comment in comments
        ]

        return paginated_response(result, total, page, limit)


@router.put(
    "/{content_type}/{slug}",
    response_model=CommentResponse,
    dependencies=[Depends(validate_review_create)],
)
async def write_comment(
    args: CommentArgs,
    content_type: CommentContentTypeEnum,
    session: AsyncSession = Depends(get_session),
    parent: Comment | None = Depends(validate_parent),
    content: CommentableType = Depends(validate_content),
    author: User = Depends(validate_rate_limit),
):
    comment = await service.create_comment(
        session,
        content_type,
        content,
        author,
        args.text,
        args.review,
        parent,
    )

    comment = await service.generate_preview(session, comment)

    return CommentNode.create(path_to_uuid(comment.reference), comment)


@router.put(
    "/{comment_reference}",
    response_model=CommentResponse,
    dependencies=[Depends(validate_review_edit)],
)
async def edit_comment(
    args: CommentTextArgs,
    session: AsyncSession = Depends(get_session),
    comment: Comment = Depends(validate_comment_edit),
):
    comment = await service.edit_comment(
        session,
        comment,
        args.text,
        args.review,
    )

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


# DEPRECATED
@router.get("/latest", response_model=list[CommentResponse])
async def latest_comments(session: AsyncSession = Depends(get_session)):
    comments = await service.latest_comments(session)
    return [
        CommentNode.create(path_to_uuid(comment.reference), comment)
        for comment in comments
    ]


# DEPRECATED
@router.get("/list", response_model=CommentListResponse)
async def comments_list(
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
    request_user: User = Depends(
        auth_required(
            scope=[constants.SCOPE_READ_COMMENT_SCORE],
            optional=True,
        )
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
