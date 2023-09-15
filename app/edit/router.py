from app.dependencies import get_page, auth_required
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import ContentEdit, User
from fastapi import APIRouter, Depends
from app.database import get_session
from app import constants
from . import service

from app.utils import (
    pagination_dict,
    pagination,
)

from .dependencies import (
    validate_edit_content_type,
    validate_edit_approval,
    validate_content_slug,
    validate_edit_id,
    validate_args,
)

from .schemas import (
    EditListResponse,
    ContentTypeEnum,
    AnimeEditArgs,
    EditResponse,
)


router = APIRouter(prefix="/edit", tags=["Edit"])


@router.get("/{edit_id}", response_model=EditResponse)
async def get_edit(edit: ContentEdit = Depends(validate_edit_id)):
    return edit


@router.get("/{content_type}/{slug}/list", response_model=EditListResponse)
async def get_edit_list(
    page: int = Depends(get_page),
    session: AsyncSession = Depends(get_session),
    content_id: str = Depends(validate_content_slug),
):
    limit, offset = pagination(page)
    total = await service.count_edits(session, content_id)
    edits = await service.get_edits(session, content_id, limit, offset)

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": edits.all(),
    }


# ToDo: Split this endpoint for all content types
@router.post("/{content_type}/{slug}", response_model=EditResponse)
async def edit_content(
    content_type: ContentTypeEnum,
    args: AnimeEditArgs = Depends(validate_args),
    session: AsyncSession = Depends(get_session),
    content_id: str = Depends(validate_content_slug),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_CREATE_EDIT])
    ),
):
    return await service.create_pending_edit(
        session, args, content_id, content_type, user
    )


@router.post("/{edit_id}/approve", response_model=EditResponse)
async def approve_edit(
    edit: ContentEdit = Depends(validate_edit_approval),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_ACCEPT_EDIT])
    ),
):
    return await service.approve_pending_edit(user, edit, session)


@router.post("/{edit_id}/deny", response_model=EditResponse)
async def deny_edit(
    edit: ContentEdit = Depends(validate_edit_content_type),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_REJECT_EDIT])
    ),
):
    return await service.deny_pending_edit(user, edit, session)


# ToDo: cancel edit
