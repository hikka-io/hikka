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
    validate_edit_approval,
    validate_content_slug,
    validate_edit_close,
    validate_edit_args,
    validate_edit_id,
)

from .schemas import (
    EditListResponse,
    ContentTypeEnum,
    EditResponse,
    EditArgs,
)


router = APIRouter(prefix="/edit", tags=["Edit"])


@router.get("/{edit_id}", response_model=EditResponse)
async def get_edit(edit: ContentEdit = Depends(validate_edit_id)):
    return edit


@router.get("/{content_type}/{slug}/list", response_model=EditListResponse)
async def get_edit_list(
    content_id: str = Depends(validate_content_slug),
    session: AsyncSession = Depends(get_session),
    page: int = Depends(get_page),
):
    limit, offset = pagination(page)
    total = await service.count_edits(session, content_id)
    edits = await service.get_edits(session, content_id, limit, offset)

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": edits.all(),
    }


@router.put("/{content_type}/{slug}", response_model=EditResponse)
async def create_edit(
    content_type: ContentTypeEnum,
    content_id: str = Depends(validate_content_slug),
    session: AsyncSession = Depends(get_session),
    args: EditArgs = Depends(validate_edit_args),
    author: User = Depends(
        auth_required(permissions=[constants.PERMISSION_CREATE_EDIT])
    ),
):
    return await service.create_pending_edit(
        session, content_type, content_id, args, author
    )


@router.post("/{edit_id}/close", response_model=EditResponse)
async def close_edit(
    edit: ContentEdit = Depends(validate_edit_close),
    session: AsyncSession = Depends(get_session),
):
    return await service.close_pending_edit(session, edit)


@router.post("/{edit_id}/approve", response_model=EditResponse)
async def approve_edit(
    edit: ContentEdit = Depends(validate_edit_approval),
    session: AsyncSession = Depends(get_session),
    moderator: User = Depends(
        auth_required(permissions=[constants.PERMISSION_ACCEPT_EDIT])
    ),
):
    return await service.approve_pending_edit(session, edit, moderator)


# @router.post("/{edit_id}/deny", response_model=EditResponse)
# async def deny_edit(
#     edit: ContentEdit = Depends(validate_edit_content_type),
#     session: AsyncSession = Depends(get_session),
#     moderator: User = Depends(
#         auth_required(permissions=[constants.PERMISSION_REJECT_EDIT])
#     ),
# ):
#     return await service.deny_pending_edit(session, edit, moderator)


# ToDo: edit list
# ToDo: fix approve
# ToDo: fix deny
# ToDo: update edit
