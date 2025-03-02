from .schemas import UploadMetadata, UploadTypeEnum
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from app.database import get_session
from fastapi import UploadFile, File
from .utils import get_mime_type
from app.errors import Abort
from app.models import User
from fastapi import Depends
from app import constants
from io import BytesIO
from app import utils
from . import service
import imagesize


async def validate_upload_rate_limit(
    upload_type: UploadTypeEnum,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(auth_required(scope=[constants.SCOPE_UPLOAD])),
):
    upload_permissions = None

    if upload_type == constants.UPLOAD_AVATAR:
        upload_permissions = [constants.PERMISSION_UPLOAD_AVATAR]

    if upload_type == constants.UPLOAD_COVER:
        upload_permissions = [constants.PERMISSION_UPLOAD_COVER]

    if upload_type == constants.UPLOAD_ATTACHMENT:
        upload_permissions = [constants.PERMISSION_UPLOAD_ATTACHMENT]

    if not upload_permissions:
        raise Abort("upload", "missconfigured-permission")

    # We check upload permissions here and not in dependency
    # Becaue we need extra logic to decide what is being uploaded
    if not utils.check_user_permissions(user, upload_permissions):
        raise Abort("permission", "denied")

    # Count uploads by given upload type
    count = await service.count_uploads_last_day(session, user, upload_type)

    # TODO: make this dynamic based on upload type (?)
    # TODO: especially for attachments!
    max_daily_uploads = 10

    if (
        user.role
        not in [
            constants.ROLE_ADMIN,
            constants.ROLE_MODERATOR,
        ]
        and count >= max_daily_uploads
    ):
        raise Abort("upload", "rate-limit")

    return user


async def validate_upload_file(
    upload_type: UploadTypeEnum, file: UploadFile = File()
) -> UploadMetadata:
    # TODO: we probably need to reduce file size here
    if file.size > 2 * 1024 * 1024:  # 2mb
        raise Abort("upload", "bad-size")

    mime_type = get_mime_type(file)

    # Different upload types support different mimes
    match upload_type:
        case constants.UPLOAD_ATTACHMENT:
            supported_mimes = ["image/jpeg", "image/webp", "image/gif"]
        case _:
            supported_mimes = ["image/jpeg"]

    if mime_type not in supported_mimes:
        raise Abort("upload", "bad-mime")

    width, height = imagesize.get(BytesIO(file.file.read()))

    if upload_type == constants.UPLOAD_AVATAR:
        if width != height:
            raise Abort("upload", "not-square")

        # TODO: set specific image resolution here (?)
        if width < 160 or height < 160:
            raise Abort("upload", "bad-resolution")

        if width > 1500 or height > 1500:
            raise Abort("upload", "bad-resolution")

    if upload_type == constants.UPLOAD_COVER:
        if width != 1500 or height != 500:
            raise Abort("upload", "bad-resolution")

    if upload_type == constants.UPLOAD_ATTACHMENT:
        if width < 200 or height < 200:
            raise Abort("upload", "bad-resolution")

        if width > 2000 or height > 2000:
            raise Abort("upload", "bad-resolution")

    # TODO: add file hash check (?)

    await file.seek(0)

    return UploadMetadata(
        **{
            "mime_type": mime_type,
            "size": file.size,
            "height": height,
            "width": width,
            "file": file,
        }
    )
