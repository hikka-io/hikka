from fastapi import UploadFile, File
from .schemas import UploadMetadata
from .utils import get_mime_type
from app.errors import Abort
from app import constants
from io import BytesIO
import imagesize


async def validate_file(
    upload_type: str, file: UploadFile = File()
) -> UploadMetadata:
    if file.size > 2 * 1024 * 1024:  # 2mb
        raise Abort("upload", "bad-size")

    if upload_type == constants.UPLOAD_AVATAR:
        mime_type = get_mime_type(file)

        if mime_type not in ["image/jpeg"]:
            raise Abort("upload", "bad-mime")

        width, height = imagesize.get(BytesIO(file.file.read()))

        if width != height:
            raise Abort("upload", "not-square")

        if width < 160 or height < 160:
            raise Abort("upload", "bad-resolution")

        if width > 1500 or height > 1500:
            raise Abort("upload", "bad-resolution")

        await file.seek(0)

    else:
        raise Abort("upload", "unknown-type")

    return UploadMetadata(
        **{
            "upload_type": upload_type,
            "mime_type": mime_type,
            "size": file.size,
            "file": file,
        }
    )
