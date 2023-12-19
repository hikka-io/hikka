from fastapi import UploadFile, File
from .utils import get_mime_type
from app.errors import Abort
from io import BytesIO
import imagesize


async def validate_file(file: UploadFile = File()):
    if get_mime_type(file) not in ["image/jpeg", "image/png"]:
        raise Abort("upload", "bad-mime")

    if file.size > 2 * 1024 * 1024:  # 2mb
        raise Abort("upload", "bad-size")

    width, height = imagesize.get(BytesIO(file.file.read()))

    if width != height:
        raise Abort("upload", "not-square")

    if width < 160 or height < 160:
        raise Abort("upload", "bad-resolution")

    if width > 1500 or height > 1500:
        raise Abort("upload", "bad-resolution")

    await file.seek(0)

    return file
