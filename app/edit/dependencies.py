from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from app.models import ContentEdit, User
from app.database import get_session
from pydantic import ValidationError
from app.errors import Abort
from fastapi import Depends
from app import constants
from . import service


from .schemas import (
    ContentTypeEnum,
    PersonEditArgs,
    AnimeEditArgs,
    EditArgs,
)


async def validate_edit_id(
    edit_id: int,
    session: AsyncSession = Depends(get_session),
) -> ContentEdit:
    """Check whether ContentEdit with edit_id exists"""

    if not (edit := await service.get_edit(session, edit_id)):
        raise Abort("edit", "not-found")

    return edit


async def validate_edit_id_pending(
    edit: ContentEdit = Depends(validate_edit_id),
):
    """Ensure edit has pending status"""

    if edit.status != constants.EDIT_PENDING:
        raise Abort("edit", "not-pending")

    return edit


async def validate_edit_modify(
    edit: ContentEdit = Depends(validate_edit_id_pending),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_MODIFY_EDIT])
    ),
):
    """Check if user which is trying to modify edit it the author"""

    if user != edit.author:
        raise Abort("edit", "not-author")

    return edit


# Here we make sure that there aren't any invalid keys and that the edits
# are actually different compared to the current version
async def validate_edit_accept(
    edit: ContentEdit = Depends(validate_edit_id_pending),
    session: AsyncSession = Depends(get_session),
) -> ContentEdit:
    content = edit.content

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
        raise Abort("edit", "content-not-found")

    return content.reference


# ToDo: move this to a model_validator once we migrate to Pydantic 2
# ToDo: make sure we can get rid of this attrocity
def edit_args_hack(
    content_type: ContentTypeEnum,
    args: EditArgs,
):
    # Make sure we know how to validate proposed content changes
    schemas = {
        constants.CONTENT_PERSON: PersonEditArgs,
        constants.CONTENT_ANIME: AnimeEditArgs,
    }

    if not (schema := schemas.get(content_type)):
        raise Abort("edit", "wrong-content-type")

    # Validate after field with provided schema
    # This checks heavily depends on Pydantic's Extra.forbid option
    try:
        schema(**args.after)
    except ValidationError:
        raise Abort("edit", "bad-edit")

    # User must propose at least some changes
    if args.after == {}:
        raise Abort("edit", "empty-edit")

    return args


# ToDo: get rid of this as well
async def validate_edit_args(
    content_type: ContentTypeEnum,
    args: EditArgs,
) -> EditArgs:
    """Validate proposed changes based on content_type"""

    return edit_args_hack(content_type, args)


async def validate_edit_args_update(
    args: EditArgs,
    edit: ContentEdit = Depends(validate_edit_modify),
):
    """Validate updating of pending edit"""

    return edit_args_hack(edit.content_type, args)
