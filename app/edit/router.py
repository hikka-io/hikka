from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app.models import Edit, User
from app import constants
from . import service

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
    validate_edit_create_args,
    validate_edit_update_args,
    validate_edit_id_pending,
    validate_content_slug,
    validate_edit_accept,
    validate_edit_modify,
    validate_edit_id,
)

from .schemas import (
    EditListResponse,
    ContentTypeEnum,
    EditResponse,
    EditArgs,
)


router = APIRouter(prefix="/edit", tags=["Edit"])


@router.get("/{content_type}/{slug}/list", response_model=EditListResponse)
async def get_content_edit_list(
    session: AsyncSession = Depends(get_session),
    content_id: str = Depends(validate_content_slug),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.count_edits_by_content_id(session, content_id)
    edits = await service.get_edits_by_content_id(
        session, content_id, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": edits.all(),
    }


@router.get("/list", response_model=EditListResponse)
async def get_edit_list(
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
    size: int = Depends(get_size),
):
    limit, offset = pagination(page, size)
    total = await service.count_edits(session)
    edits = await service.get_edits(session, limit, offset)

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": edits.all(),
    }


@router.get("/{edit_id}", response_model=EditResponse)
async def get_edit(edit: Edit = Depends(validate_edit_id)):
    return edit


@router.put("/{content_type}/{slug}", response_model=EditResponse)
async def create_edit(
    content_type: ContentTypeEnum,
    session: AsyncSession = Depends(get_session),
    args: EditArgs = Depends(validate_edit_create_args),
    content_id: str = Depends(validate_content_slug),
    author: User = Depends(
        auth_required(permissions=[constants.PERMISSION_CREATE_EDIT])
    ),
    _: bool = Depends(check_captcha),
):
    return await service.create_pending_edit(
        session, content_type, content_id, args, author
    )


@router.post("/{edit_id}/update", response_model=EditResponse)
async def update_edit(
    session: AsyncSession = Depends(get_session),
    args: EditArgs = Depends(validate_edit_update_args),
    edit: Edit = Depends(validate_edit_modify),
    _: bool = Depends(check_captcha),
):
    return await service.update_pending_edit(session, edit, args)


@router.post("/{edit_id}/close", response_model=EditResponse)
async def close_edit(
    session: AsyncSession = Depends(get_session),
    edit: Edit = Depends(validate_edit_modify),
):
    return await service.close_pending_edit(session, edit)


@router.post("/{edit_id}/accept", response_model=EditResponse)
async def accept_edit(
    session: AsyncSession = Depends(get_session),
    edit: Edit = Depends(validate_edit_accept),
    moderator: User = Depends(
        auth_required(permissions=[constants.PERMISSION_ACCEPT_EDIT])
    ),
):
    return await service.accept_pending_edit(session, edit, moderator)


@router.post("/{edit_id}/deny", response_model=EditResponse)
async def deny_edit(
    session: AsyncSession = Depends(get_session),
    edit: Edit = Depends(validate_edit_id_pending),
    moderator: User = Depends(
        auth_required(permissions=[constants.PERMISSION_ACCEPT_EDIT])
    ),
):
    return await service.deny_pending_edit(session, edit, moderator)
