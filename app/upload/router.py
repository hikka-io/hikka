from fastapi import APIRouter, UploadFile, Depends
from .dependencies import validate_file
from . import service


router = APIRouter(prefix="/upload", tags=["Upload"])


@router.put("/image")
async def upload_image(file: UploadFile = Depends(validate_file)):
    return await service.upload_image(file)
