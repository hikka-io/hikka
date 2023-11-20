from app.dependencies import auth_required, get_user
from fastapi import APIRouter, Depends
from app.schemas import UserResponse
from app.models import User


router = APIRouter(prefix="/user", tags=["User"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Logged user profile",
)
async def profile(user: User = Depends(auth_required())):
    return user


@router.get(
    "/{username}",
    response_model=UserResponse,
    summary="User profile",
)
async def user_profile(user: User = Depends(get_user)):
    return user
