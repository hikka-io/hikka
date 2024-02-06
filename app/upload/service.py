from .schemas import UploadMetadata, UploadTypeEnum
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Image, Upload
from sqlalchemy import select, func
from app.service import create_log
from app.utils import get_settings
from datetime import datetime
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
    today = utils.round_day(datetime.now())
    return await session.scalar(
        select(func.count(Upload.id)).filter(
            Upload.user == user,
            Upload.created > today,
            Upload.type == upload_type,
        )
    )


async def process_upload_file(
    session: AsyncSession,
    upload_type: UploadTypeEnum,
    upload_metadata: UploadMetadata,
    user: User,
) -> Image:
    extension = utils.get_mime_extension(upload_metadata.mime_type)

    file_path = (
        f"/uploads/{user.username}/{upload_type}/{str(uuid4())}.{extension}"
    )

    now = datetime.utcnow()

    image = Image(
        **{
            "path": file_path,
            "uploaded": False,
            "ignore": False,
            "created": now,
        }
    )

    upload = Upload(
        **{
            "mime_type": upload_metadata.mime_type,
            "size": upload_metadata.size,
            "type": upload_type,
            "path": file_path,
            "created": now,
            "image": image,
            "user": user,
        }
    )

    image.uploaded = await s3_upload_file(upload_metadata, file_path)

    if image.uploaded:
        if upload_type == constants.UPLOAD_AVATAR:
            # Mark old image to be deleted
            if user.avatar_image_relation:
                user.avatar_image_relation.deletion_request = True

            # Only update image relation if file has been uploaded
            user.avatar_image_relation = image

        if upload_type == constants.UPLOAD_COVER:
            # Mark old image to be deleted
            if user.cover_image_relation:
                user.cover_image_relation.deletion_request = True

            # Only update image relation if file has been uploaded
            user.cover_image_relation = image

    session.add_all([image, upload])
    await session.commit()

    await create_log(
        session,
        constants.LOG_UPLOAD,
        user,
        upload.id,
    )

    return image
