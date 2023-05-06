from .schemas import UserResponse, DescriptionArgs
from app.dependencies import auth_required
from fastapi import APIRouter, Depends
from .dependencies import get_profile
from app.models import User
from app import display


router = APIRouter(prefix="/user")


@router.get("/me", response_model=UserResponse)
async def profile(user: User = Depends(auth_required)):
    return display.user(user)


@router.get("/{username}", response_model=UserResponse)
async def user_profile(user: User = Depends(get_profile)):
    return display.user(user)


# ToDo: move to user settings
@router.post("/description", response_model=UserResponse)
async def change_description(
    args: DescriptionArgs, user: User = Depends(auth_required)
):
    user.description = args.description
    await user.save()

    return display.user(user)
