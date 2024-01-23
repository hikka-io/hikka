from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_session
from fastapi import APIRouter, Depends
from app.models import User
from . import service

from .dependencies import (
    validate_upload_rate_limit,
    validate_upload_file,
)

from .schemas import (
    UploadMetadata,
    UploadTypeEnum,
    ImageResponse,
)


router = APIRouter(prefix="/upload", tags=["Upload"])


@router.put(
    "/{upload_type}",
    response_model=ImageResponse,
)
async def upload_image(
    upload_type: UploadTypeEnum,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(validate_upload_rate_limit),
    upload_metadata: UploadMetadata = Depends(validate_upload_file),
):
    return await service.process_upload_file(
        session, upload_type, upload_metadata, user
    )
