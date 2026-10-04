from app.admin.dependencies import validate_update_user
from app.dependencies import auth_required, get_user
from app.common.schemas.user import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.admin.schemas import UpdateUserBody
from fastapi import APIRouter, Depends
from app.database import get_session
from app.admin import service
from app.models import User
from app import constants


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.patch(
    "/user/{username}",
    summary="Update user",
    response_model=UserResponse,
    operation_id="admin_update_user",
    dependencies=[
        Depends(auth_required([constants.PERMISSION_ADMIN_UPDATE_USER]))
    ],
)
async def update_user(
    body: UpdateUserBody = Depends(validate_update_user),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user),
):
    return await service.update_user(session, user, body)
