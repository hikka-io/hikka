from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from app.database import get_session
from fastapi import UploadFile, File
from .schemas import UploadMetadata
from .utils import get_mime_type
from app.errors import Abort
from app.models import User
from fastapi import Depends
from app import constants
from io import BytesIO
from . import service
import imagesize


async def validate_rate_limit(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        auth_required(permissions=[constants.PERMISSION_UPLOAD_AVATAR])
    ),
):
    count = await service.count_uploads_last_day(session, user)

    if (
        user.role
        not in [
            constants.ROLE_ADMIN,
            constants.ROLE_MODERATOR,
        ]
        and count >= 10
    ):
        raise Abort("upload", "rate-limit")

    return user


async def validate_avatar_file(file: UploadFile = File()) -> UploadMetadata:
    # ToDo: we probably need to reduce file size here
    if file.size > 2 * 1024 * 1024:  # 2mb
        raise Abort("upload", "bad-size")

    mime_type = get_mime_type(file)

    if mime_type not in ["image/jpeg"]:
        raise Abort("upload", "bad-mime")

    width, height = imagesize.get(BytesIO(file.file.read()))

    if width != height:
        raise Abort("upload", "not-square")

    # ToDo: set specific image resolution here (?)
    if width < 160 or height < 160:
        raise Abort("upload", "bad-resolution")

    if width > 1500 or height > 1500:
        raise Abort("upload", "bad-resolution")

    # ToDo: add file hash check

    await file.seek(0)

    return UploadMetadata(
        **{
            "mime_type": mime_type,
            "size": file.size,
            "file": file,
        }
    )
