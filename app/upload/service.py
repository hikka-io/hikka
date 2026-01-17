from .schemas import UploadMetadata, UploadTypeEnum
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import get_settings, utcnow
from sqlalchemy import select, func
from app.service import create_log
from app.models import User, Image
from app import constants
from uuid import uuid4
from . import utils
import aioboto3


async def s3_upload_file(upload_metadata: UploadMetadata, file_path: str):
    settings = get_settings()
    boto_session = aioboto3.Session()

    async with boto_session.client(
        "s3",
        endpoint_url=settings.s3.endpoint,
        aws_access_key_id=settings.s3.key,
        aws_secret_access_key=settings.s3.secret,
    ) as s3:
        try:
            path = file_path.lstrip("/")

            await s3.upload_fileobj(
                upload_metadata.file.file,
                settings.s3.bucket,
                path,
                ExtraArgs={
                    "ContentType": upload_metadata.mime_type,
                },
            )

        except Exception:
            return False

    return True


async def count_uploads_last_day(
    session: AsyncSession, user: User, upload_type: UploadTypeEnum
):
    today = utils.round_day(utcnow())

    return await session.scalar(
        select(func.count(Image.id)).filter(
            Image.user == user,
            Image.created > today,
            Image.type == upload_type,
        )
    )


async def process_upload_file(
    session: AsyncSession,
    upload_type: UploadTypeEnum,
    upload_metadata: UploadMetadata,
    user: User,
) -> Image:
    extension = utils.get_mime_extension(upload_metadata.mime_type)

    file_path = f"/uploads/{user.username}/{upload_type.name}/{str(uuid4())}.{extension}"

    now = utcnow()

    image = Image(
        **{
            "mime_type": upload_metadata.mime_type,
            "height": upload_metadata.height,
            "width": upload_metadata.width,
            "size": upload_metadata.size,
            "type": upload_type,
            "user_id": user.id,
            "path": file_path,
            "uploaded": False,
            "ignore": False,
            "system": False,
            "created": now,
        }
    )

    image.uploaded = await s3_upload_file(upload_metadata, file_path)

    if image.uploaded:
        if upload_type == constants.UPLOAD_AVATAR:
            # Mark old image to be deleted
            if user.avatar_image:
                user.avatar_image.deletion_request = True

            # Only update image relation if file has been uploaded
            user.avatar_image = image

        if upload_type == constants.UPLOAD_COVER:
            # Mark old image to be deleted
            if user.cover_image:
                user.cover_image.deletion_request = True

            # Only update image relation if file has been uploaded
            user.cover_image = image

        if upload_type == constants.UPLOAD_ATTACHMENT:
            image.used = False

    session.add_all([image])
    await session.commit()

    await create_log(
        session,
        constants.LOG_UPLOAD,
        user,
        image.id,
        data={"upload_type": upload_type},
    )

    return image
