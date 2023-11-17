from app.dependencies import get_page, auth_required
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Edit, User
from fastapi import APIRouter, Depends
from app.database import get_session
from app import constants
from . import service

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
    content_id: str = Depends(validate_content_slug),
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
):
    limit, offset = pagination(page)
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
):
    limit, offset = pagination(page)
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
    args: EditArgs = Depends(validate_edit_create_args),
    content_id: str = Depends(validate_content_slug),
    session: AsyncSession = Depends(get_session),
    author: User = Depends(
        auth_required(permissions=[constants.PERMISSION_CREATE_EDIT])
    ),
):
    return await service.create_pending_edit(
        session, content_type, content_id, args, author
    )


@router.post("/{edit_id}/update", response_model=EditResponse)
async def update_edit(
    args: EditArgs = Depends(validate_edit_update_args),
    edit: Edit = Depends(validate_edit_modify),
    session: AsyncSession = Depends(get_session),
):
    return await service.update_pending_edit(session, edit, args)


@router.post("/{edit_id}/close", response_model=EditResponse)
async def close_edit(
    edit: Edit = Depends(validate_edit_modify),
    session: AsyncSession = Depends(get_session),
):
    return await service.close_pending_edit(session, edit)


@router.post("/{edit_id}/accept", response_model=EditResponse)
async def accept_edit(
    edit: Edit = Depends(validate_edit_accept),
    session: AsyncSession = Depends(get_session),
    moderator: User = Depends(
        auth_required(permissions=[constants.PERMISSION_ACCEPT_EDIT])
    ),
):
    return await service.accept_pending_edit(session, edit, moderator)


@router.post("/{edit_id}/deny", response_model=EditResponse)
async def deny_edit(
    edit: Edit = Depends(validate_edit_id_pending),
    session: AsyncSession = Depends(get_session),
    moderator: User = Depends(
        auth_required(permissions=[constants.PERMISSION_ACCEPT_EDIT])
    ),
):
    return await service.deny_pending_edit(session, edit, moderator)
