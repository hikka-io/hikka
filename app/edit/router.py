from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, ContentEdit
from fastapi import APIRouter, Depends
from app.dependencies import get_page
from app.database import get_session
from . import service

from app.utils import (
    pagination_dict,
    pagination,
)

from .dependencies import (
    validate_edit_content_type,
    validate_edit_approval,
    validate_content_slug,
    validate_review_perms,
    validate_edit_perms,
    validate_edit_id,
    validate_args,
)


from .schemas import (
    EditListResponse,
    ContentTypeEnum,
    EditResponse,
    AnimeEditArgs,
    # EditArgs,
)


router = APIRouter(prefix="/edit", tags=["Edit"])


@router.get(
    "/{edit_id}",
    response_model=EditResponse,
)
async def get_edit(
    edit: ContentEdit = Depends(validate_edit_id),
):
    return edit


@router.get(
    "/{content_type}/{slug}/list",
    response_model=EditListResponse,
)
async def get_edit_list(
    page: int = Depends(get_page),
    content=Depends(validate_content_slug),
    session: AsyncSession = Depends(get_session),
):
    limit, offset = pagination(page)
    total = await service.count_edits_by_content_id(session, content.id)
    result = await service.get_edits_by_content_id(
        session, content.id, limit, offset
    )

    return {
        "pagination": pagination_dict(total, page, limit),
        "list": [entry for entry in result],
    }


# ToDo: Split this endpoint for all content types
@router.post(
    "/{content_type}/{slug}",
    response_model=EditResponse,
)
async def edit_anime_content(
    content_type: ContentTypeEnum,
    args: AnimeEditArgs = Depends(validate_args),
    user: User = Depends(validate_edit_perms),
    content=Depends(validate_content_slug),
    session: AsyncSession = Depends(get_session),
):
    return await service.create_edit_request(
        args, content.id, content_type, user, session
    )


@router.post(
    "/{content_type}/{edit_id}/approve",
    response_model=EditResponse,
)
async def approve_anime_edit(
    content_type: ContentTypeEnum,
    user: User = Depends(validate_review_perms),
    edit: ContentEdit = Depends(validate_edit_approval),
    session: AsyncSession = Depends(get_session),
):
    return await service.approve_edit_request(user, edit, session)


@router.post(
    "/{content_type}/{edit_id}/deny",
    response_model=EditResponse,
)
async def deny_anime_edit(
    user: User = Depends(validate_review_perms),
    edit: ContentEdit = Depends(validate_edit_content_type),
    session: AsyncSession = Depends(get_session),
):
    return await service.deny_anime_edit_request(user, edit, session)
