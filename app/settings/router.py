from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from fastapi import APIRouter, Depends
from app.database import get_session
from app.schemas import UserResponse
from .schemas import DescriptionArgs
from app.models import User
from . import service


router = APIRouter(prefix="/settings", tags=["Settings"])


@router.post(
    "/description",
    response_model=UserResponse,
    summary="Change user description",
)
async def change_description(
    args: DescriptionArgs,
    user: User = Depends(auth_required()),
    session: AsyncSession = Depends(get_session),
):
    return await service.change_description(session, user, args.description)
