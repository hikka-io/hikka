from fastapi import Depends

from app.admin.schemas import UpdateUserBody
from app.dependencies import get_user
from app.errors import Abort
from app.models import User


async def validate_update_user(
    body: UpdateUserBody,
    user: User = Depends(get_user),
):
    """
    Validate body of the update user request.

    - Too many return-statements?
    """

    if body.forbid_actions is not None:
        user_forbidden_actions = set(user.forbidden_actions)
        body_forbidden_actions = set(body.forbid_actions)

        # Merge changes nothing if user already has all passed actions
        if body.forbid_actions_merge:
            changed = not user_forbidden_actions.issuperset(
                body_forbidden_actions
            )
        else:
            changed = user_forbidden_actions != body_forbidden_actions

        if changed:
            return body

    if body.remove_avatar and user.avatar_image_id is not None:
        return body

    if body.remove_cover and user.cover_image_id is not None:
        return body

    if body.description is not None and body.description != user.description:
        return body

    if body.remove_description and user.description is not None:
        return body

    if body.banned is not None and user.banned != body.banned:
        return body

    raise Abort("admin", "nothing_to_update")
