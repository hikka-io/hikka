from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import validate_set_username
from app.dependencies import auth_required
from fastapi import APIRouter, Depends
from app.database import get_session
from .schemas import DescriptionArgs
from app.models import User
from . import service

from app.schemas import (
    UserResponse,
    UsernameArgs,
)


router = APIRouter(prefix="/settings", tags=["Settings"])


@router.post(
    "/description",
    response_model=UserResponse,
    summary="Change description",
)
async def change_description(
    args: DescriptionArgs,
    user: User = Depends(auth_required()),
    session: AsyncSession = Depends(get_session),
):
    return await service.change_description(session, user, args.description)


@router.put(
    "/username",
    response_model=UserResponse,
    summary="Change username",
)
async def username(
    args: UsernameArgs = Depends(validate_set_username),
    user: User = Depends(auth_required()),
    session: AsyncSession = Depends(get_session),
):
    return await service.set_username(session, user, args.username)


# @router.put(
#     "/email",
#     response_model=UserResponse,
#     summary="Set a email",
# )
# async def email(
#     args: EmailArgs = Depends(validate_set_email),
#     user: User = Depends(auth_required()),
#     session: AsyncSession = Depends(get_session),
# ):
#     user = await service.set_email(session, user, args.email)
#     user = await service.create_activation_token(session, user)

#     # Add new activation email to database
#     await service.create_email(
#         session,
#         constants.EMAIL_ACTIVATION,
#         user.activation_token,
#         user,
#     )

#     return user
