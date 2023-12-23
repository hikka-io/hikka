from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Image, Upload
from .schemas import UploadMetadata
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


async def process_avatar_upload(
    session: AsyncSession,
    upload_metadata: UploadMetadata,
    user: User,
) -> Image:
    extension = utils.get_mime_extension(upload_metadata.mime_type)

    file_path = f"/uploads/{user.username}/avatar/{str(uuid4())}.{extension}"

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
            "type": constants.UPLOAD_AVATAR,
            "size": upload_metadata.size,
            "path": file_path,
            "created": now,
            "image": image,
            "user": user,
        }
    )

    image.uploaded = await s3_upload_file(upload_metadata, file_path)

    user.avatar_image_relation = image

    session.add_all([image, upload])
    await session.commit()

    return image
