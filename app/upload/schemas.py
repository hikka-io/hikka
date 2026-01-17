from app.schemas import CustomModel
from fastapi import UploadFile
from app import constants
from enum import Enum


# Enums
class UploadTypeEnum(str, Enum):
    attachment = constants.UPLOAD_ATTACHMENT
    avatar = constants.UPLOAD_AVATAR
    cover = constants.UPLOAD_COVER


# Responses
class ImageResponse(CustomModel):
    url: str


# Misc
class UploadMetadata(CustomModel):
    file: UploadFile
    mime_type: str
    height: int
    width: int
    size: int
