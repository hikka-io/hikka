from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import validate_avatar_file
from app.dependencies import auth_required
from app.dependencies import get_session
from fastapi import APIRouter, Depends
from app.models import User
from . import service

from .schemas import (
    UploadMetadata,
    ImageResponse,
)


router = APIRouter(prefix="/upload", tags=["Upload"])


@router.put("/avatar", response_model=ImageResponse)
async def upload_image(
    session: AsyncSession = Depends(get_session),
    upload_metadata: UploadMetadata = Depends(validate_avatar_file),
    user: User = Depends(auth_required()),
):
    return await service.process_avatar_upload(
        session,
        upload_metadata,
        user,
    )
