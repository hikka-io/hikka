from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from app.admin.dependencies import require_user, validate_update_user
from app.admin.schemas import UpdateUserBody
from app.dependencies import auth_required
from app.database import get_session
from app.schemas import UserResponse
from app.admin import service
from app.models import User
from app import constants

router = APIRouter(prefix="/admin", tags=["Admin"])

# region User related endpoints


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
    user: User = Depends(require_user),
):
    return await service.update_user(session, user, body)


# endregion
