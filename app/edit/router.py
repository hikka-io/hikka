from app.dependencies import get_page, auth_required
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database import get_session
from app import constants
from typing import Union
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

from app.models import (
    AnimeStaffRole,
    ContentEdit,
    AnimeGenre,
    Character,
    Company,
    Person,
    Anime,
    User,
)


router = APIRouter(prefix="/edit", tags=["Edit"])


@router.get("/{edit_id}", response_model=EditResponse)
async def get_edit(edit: ContentEdit = Depends(validate_edit_id)):
    return edit


@router.get("/{content_type}/{slug}/list", response_model=EditListResponse)
async def get_edits_list(
    page: int = Depends(get_page),
    session: AsyncSession = Depends(get_session),
    content: Union[
        Anime, Character, Company, AnimeGenre, Person, AnimeStaffRole
    ] = Depends(validate_content_slug),
):
    limit, offset = pagination(page)
    total = await service.count_edits_by_content_id(session, content.id)
    edits = await service.get_edits_by_content_id(
        session, content.id, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": edits.all(),
    }


# ToDo: Split this endpoint for all content types
@router.post("/{content_type}/{slug}", response_model=EditResponse)
async def edit_anime_content(
    content_type: ContentTypeEnum,
    args: AnimeEditArgs = Depends(validate_args),
    session: AsyncSession = Depends(get_session),
    content: Union[
        Anime, Character, Company, AnimeGenre, Person, AnimeStaffRole
    ] = Depends(validate_content_slug),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_CREATE_EDIT])
    ),
):
    return await service.create_edit_request(
        session, args, content.id, content_type, user
    )


@router.post("/{edit_id}/approve", response_model=EditResponse)
async def approve_anime_edit(
    edit: ContentEdit = Depends(validate_edit_approval),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_ACCEPT_EDIT])
    ),
):
    return await service.approve_edit_request(user, edit, session)


@router.post("/{edit_id}/deny", response_model=EditResponse)
async def deny_anime_edit(
    edit: ContentEdit = Depends(validate_edit_content_type),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_REJECT_EDIT])
    ),
):
    return await service.deny_anime_edit_request(user, edit, session)
