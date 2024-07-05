from sqlalchemy.ext.asyncio import AsyncSession
from app.manga.schemas import MangaPaginationResponse
from app.novel.schemas import NovelPaginationResponse
from app.schemas import AnimePaginationResponse
from fastapi import APIRouter, Depends
from app.database import get_session
from app import constants
from . import service

from app.models import (
    Character,
    Person,
    Anime,
    Manga,
    Novel,
    User,
    Edit,
)

from app.dependencies import (
    auth_required,
    check_captcha,
    get_page,
    get_size,
)

from app.utils import (
    pagination_dict,
    pagination,
)

from .dependencies import (
    validate_edit_search_args,
    validate_edit_update_args,
    validate_edit_id_pending,
    validate_edit_create,
    validate_edit_accept,
    validate_edit_update,
    validate_edit_close,
    validate_content,
    validate_edit_id,
)

from .schemas import (
    ContentToDoEnum,
    EditContentToDoEnum,
    EditContentTypeEnum,
    EditListResponse,
    EditSearchArgs,
    EditResponse,
    EditArgs,
)


router = APIRouter(prefix="/edit", tags=["Edit"])


@router.post("/list", response_model=EditListResponse)
async def get_edits(
    args: EditSearchArgs = Depends(validate_edit_search_args),
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.count_edits(session, args)
    edits = await service.get_edits(session, args, limit, offset)

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": edits.all(),
    }


@router.get("/{edit_id}", response_model=EditResponse)
async def get_edit(edit: Edit = Depends(validate_edit_id)):
    return edit


@router.put("/{content_type}/{slug}", response_model=EditResponse)
async def create_edit(
    content_type: EditContentTypeEnum,
    session: AsyncSession = Depends(get_session),
    content: Person | Anime | Manga | Novel | Character = Depends(
        validate_content
    ),
    args: EditArgs = Depends(validate_edit_create),
    author: User = Depends(
        auth_required(permissions=[constants.PERMISSION_EDIT_CREATE])
    ),
    _: bool = Depends(check_captcha),
):
    return await service.create_pending_edit(
        session, content_type, content, args, author
    )


@router.post("/{edit_id}/update", response_model=EditResponse)
async def update_edit(
    session: AsyncSession = Depends(get_session),
    args: EditArgs = Depends(validate_edit_update_args),
    edit: Edit = Depends(validate_edit_update),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_EDIT_UPDATE])
    ),
    _: bool = Depends(check_captcha),
):
    return await service.update_pending_edit(session, edit, user, args)


@router.post("/{edit_id}/close", response_model=EditResponse)
async def close_edit(
    session: AsyncSession = Depends(get_session),
    edit: Edit = Depends(validate_edit_close),
):
    return await service.close_pending_edit(session, edit)


@router.post("/{edit_id}/accept", response_model=EditResponse)
async def accept_edit(
    session: AsyncSession = Depends(get_session),
    edit: Edit = Depends(validate_edit_accept),
    moderator: User = Depends(
        auth_required(permissions=[constants.PERMISSION_EDIT_ACCEPT])
    ),
):
    return await service.accept_pending_edit(session, edit, moderator)


@router.post("/{edit_id}/deny", response_model=EditResponse)
async def deny_edit(
    session: AsyncSession = Depends(get_session),
    edit: Edit = Depends(validate_edit_id_pending),
    moderator: User = Depends(
        auth_required(permissions=[constants.PERMISSION_EDIT_ACCEPT])
    ),
):
    return await service.deny_pending_edit(session, edit, moderator)


@router.get(
    "/todo/{content_type}/{todo_type}",
    response_model=AnimePaginationResponse
    | MangaPaginationResponse
    | NovelPaginationResponse,
)
async def get_content_edit_todo(
    content_type: EditContentToDoEnum,
    todo_type: ContentToDoEnum,
    session: AsyncSession = Depends(get_session),
    request_user: User | None = Depends(auth_required(optional=True)),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.content_todo_total(session, content_type, todo_type)
    content = await service.content_todo(
        session, content_type, todo_type, request_user, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": content.unique().all(),
    }
