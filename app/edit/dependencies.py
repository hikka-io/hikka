from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import check_user_permissions
from app.dependencies import auth_required
from app.database import get_session
from app.errors import Abort
from fastapi import Depends
from app import constants
from . import service
from . import utils

from app.service import (
    get_user_by_username,
    get_content_by_slug,
)

from app.models import (
    Person,
    Anime,
    Edit,
    User,
)

from .schemas import (
    EditContentTypeEnum,
    EditSearchArgs,
    EditArgs,
)


async def validate_edit_search_args(
    args: EditSearchArgs,
    session: AsyncSession = Depends(get_session),
):
    if args.author:
        if not await get_user_by_username(session, args.author):
            raise Abort("edit", "author-not-found")

    if args.moderator:
        if not await get_user_by_username(session, args.moderator):
            raise Abort("edit", "moderator-not-found")

    if args.slug:
        if not args.content_type:
            raise Abort("edit", "missing-content-type")

        if not await get_content_by_slug(
            session,
            args.content_type,
            args.slug,
        ):
            raise Abort("edit", "content-not-found")

    return args


async def validate_edit_id(
    edit_id: int,
    session: AsyncSession = Depends(get_session),
) -> Edit:
    """Check whether Edit with edit_id exists"""

    if not (edit := await service.get_edit(session, edit_id)):
        raise Abort("edit", "not-found")

    return edit


async def validate_edit_id_pending(
    edit: Edit = Depends(validate_edit_id),
):
    """Ensure edit has pending status"""

    if edit.status != constants.EDIT_PENDING:
        raise Abort("edit", "not-pending")

    return edit


async def validate_edit_update(
    edit: Edit = Depends(validate_edit_id_pending),
    user: User = Depends(auth_required()),
):
    """Check if user which is trying to update edit it the author
    or moderator"""

    if user != edit.author and not check_user_permissions(
        user, [constants.PERMISSION_EDIT_UPDATE_MODERATOR]
    ):
        raise Abort("permission", "denied")

    return edit


async def validate_edit_close(
    edit: Edit = Depends(validate_edit_id_pending),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_EDIT_CLOSE])
    ),
):
    """Check if user which is trying to close edit it the author"""

    if user != edit.author:
        raise Abort("edit", "not-author")

    return edit


# Here we make sure that there aren't any invalid keys and that the edits
# are actually different compared to the current version
async def validate_edit_accept(
    edit: Edit = Depends(validate_edit_id_pending),
) -> Edit:
    """Validate edit right before accepting it"""

    if utils.check_invalid_fields(edit):
        raise Abort("edit", "invalid-field")

    new_after = utils.check_after(edit.after, edit.content)
    if len(new_after) == 0:
        raise Abort("edit", "empty-edit")

    return edit


async def validate_content(
    slug: str,
    content_type: EditContentTypeEnum,
    session: AsyncSession = Depends(get_session),
):
    if not (content := await get_content_by_slug(session, content_type, slug)):
        raise Abort("edit", "content-not-found")

    return content


async def validate_edit_create_args(
    content_type: EditContentTypeEnum,
    args: EditArgs,
) -> EditArgs:
    """Validate create edit args"""

    if not utils.check_edit_schema(content_type, args):
        raise Abort("edit", "bad-edit")

    return args


async def validate_edit_update_args(
    args: EditArgs,
    edit: Edit = Depends(validate_edit_update),
    author: User = Depends(auth_required()),
) -> EditArgs:
    """Validate update edit args"""

    if not utils.check_edit_schema(edit.content_type, args):
        raise Abort("edit", "bad-edit")

    args.after = utils.check_after(args.after, edit.content)
    if len(args.after) == 0:
        raise Abort("edit", "empty-edit")

    if args.auto and not check_user_permissions(
        author, [constants.PERMISSION_EDIT_AUTO]
    ):
        raise Abort("permission", "denied")

    return args


async def validate_edit_create(
    content: Person | Anime | None = Depends(validate_content),
    args: EditArgs = Depends(validate_edit_create_args),
    author: User = Depends(auth_required()),
):
    args.after = utils.check_after(args.after, content)
    if len(args.after) == 0:
        raise Abort("edit", "empty-edit")

    if args.auto and not check_user_permissions(
        author, [constants.PERMISSION_EDIT_AUTO]
    ):
        raise Abort("permission", "denied")

    return args
