from app.dependencies import auth_required
from fastapi import APIRouter, Depends
from .schemas import UserResponse
from app.models import User
from app import display

from .dependencies import (
    update_description,
    get_profile,
)

router = APIRouter(prefix="/user")


@router.get("/me", response_model=UserResponse)
async def profile(user: User = Depends(auth_required)):
    return display.user(user)


@router.get("/{username}", response_model=UserResponse)
async def user_profile(user: User = Depends(get_profile)):
    return display.user(user)


# ToDo: move to user settings
@router.post("/description", response_model=UserResponse)
async def change_description(user: User = Depends(update_description)):
    return display.user(user)
