from fastapi import APIRouter, Depends
from ..decorators import auth_required
from .responses import UserResponse
from .args import DescriptionArgs
from ..errors import Abort
from ..models import User
from .. import display

router = APIRouter(prefix="/user")


@router.get("/me", response_model=UserResponse)
async def profile(user: User = Depends(auth_required())):
    return display.user(user)


# ToDo: move to user settings
@router.post("/description", response_model=UserResponse)
async def change_description(
    args: DescriptionArgs, user: User = Depends(auth_required())
):
    user.description = args.description
    await user.save()

    return display.user(user)


@router.get("/{username}", response_model=UserResponse)
async def user_profile(username: str):
    if not (user := await User.filter(username=username).first()):
        raise Abort("user", "not-found")

    return display.user(user)
