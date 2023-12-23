from app.schemas import CustomModel
from fastapi import UploadFile


# Responses
class ImageResponse(CustomModel):
    url: str


# Misc
class UploadMetadata(CustomModel):
    file: UploadFile
    mime_type: str
    size: int
