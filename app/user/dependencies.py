from app.dependencies import auth_required
from .schemas import DescriptionArgs
from app.errors import Abort
from app.models import User
from fastapi import Depends


async def update_description(
    args: DescriptionArgs, user: User = Depends(auth_required)
) -> User:
    user.description = args.description
    await user.save()

    return user


async def get_profile(username: str) -> User:
    if not (user := await User.filter(username=username).first()):
        raise Abort("user", "not-found")

    return user
