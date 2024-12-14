from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.service import get_user_by_username
from app.admin.schemas import UpdateUserBody
from app.database import get_session
from app.errors import Abort
from app.models import User


async def require_user(
    username: str, session: AsyncSession = Depends(get_session)
):
    user = await get_user_by_username(session, username)

    if user is None:
        raise Abort("admin", "user-not-found")

    return user


async def validate_update_user(
    body: UpdateUserBody,
    user: User = Depends(require_user),
):
    """
    Validate body of the update user request.

    - Too many return-statements?
    """

    user_forbidden_actions = set(user.forbidden_actions)
    body_forbidden_actions = (
        set(body.forbid_actions) if body.forbid_actions else None
    )

    if body.forbid_actions is not None and (
        body.forbid_actions_merge
        and not user_forbidden_actions.issuperset(body_forbidden_actions)
        or user_forbidden_actions != body_forbidden_actions
    ):
        return body

    if body.remove_avatar and user.avatar_image_id is not None:
        return body

    if body.description is not None and body.description != user.description:
        return body

    if body.remove_description and user.description is not None:
        return body

    if body.banned is not None and user.banned != body.banned:
        return body

    raise Abort("admin", "nothing_to_update")
