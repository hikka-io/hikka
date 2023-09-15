from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError
from app.database import get_session
from app.models import ContentEdit
from app.errors import Abort
from fastapi import Depends
from app import constants
from . import service

from .schemas import (
    ContentTypeEnum,
    AnimeEditArgs,
    EditArgs,
)


async def validate_edit_id(
    edit_id: int, session: AsyncSession = Depends(get_session)
) -> ContentEdit:
    """Check whether ContentEdit with edit_id exists"""

    if not (edit := await service.get_edit(session, edit_id)):
        raise Abort("edit", "not-found")

    return edit


async def validate_edit_content_type(
    content_type: ContentTypeEnum,
    edit: ContentEdit = Depends(validate_edit_id),
    session: AsyncSession = Depends(get_session),
) -> ContentEdit:
    # ToDo: move this check into separate dependency
    if edit.status != constants.EDIT_PENDING:
        raise Abort("edit", "already-reviewed")

    if edit.content_type != content_type:
        raise Abort("edit", "wrong-content-type")

    if not (
        await service.get_content(
            session,
            content_type,
            edit.content_id,
        )
    ):
        raise Abort("edit", "invalid-content-id")

    return edit


# Here we make sure that there aren't any invalid keys and that the edits
# are actually different compared to the current version
async def validate_edit_approval(
    content_type: ContentTypeEnum,
    edit: ContentEdit = Depends(validate_edit_content_type),
    session: AsyncSession = Depends(get_session),
) -> ContentEdit:
    # ToDo: check if edit can be approved (pending type)

    content = await service.get_content(session, content_type, edit.content_id)

    pop_list = []

    for key, value in edit.after.items():
        if not hasattr(content, key):
            raise Abort("edit", "invalid-field")

        if getattr(content, key) == value:
            pop_list.append(key)

    for pop_key in pop_list:
        edit.after.pop(pop_key)

    if len(edit.after) <= 0:
        raise Abort("edit", "empty-edit")

    return edit


async def validate_content_slug(
    slug: str,
    content_type: ContentTypeEnum,
    session: AsyncSession = Depends(get_session),
) -> str:
    """Return content reference by content_type and slug"""

    if not (
        content := await service.get_content_by_slug(
            session, content_type, slug
        )
    ):
        # ToDo: return not-found by content type
        raise Abort("edit", "content-not-found")

    return content.reference


# ToDo: move this to a model_validator once we migrate to Pydantic 2
async def validate_edit_args(
    content_type: ContentTypeEnum, args: EditArgs
) -> EditArgs:
    """Validate proposed changes based on content_type"""

    # Make sure we know how to validate proposed content changes
    schemas = {constants.CONTENT_ANIME: AnimeEditArgs}
    if not (schema := schemas.get(content_type)):
        raise Abort("edit", "wrong-content-type")

    # Validate after field with provided schema
    try:
        args.after = schema(**args.after)
    except ValidationError:
        raise Abort("edit", "bad-edit")

    # User must propose at least some changes
    if args.after == {}:
        raise Abort("edit", "empty-edit")

    return args
