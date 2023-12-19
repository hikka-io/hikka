from app.utils import get_settings
from fastapi import UploadFile
import aioboto3


async def upload_image(file: UploadFile):
    settings = get_settings()
    boto_session = aioboto3.Session()

    async with boto_session.resource(
        "s3",
        endpoint_url=settings.s3.endpoint,
        aws_access_key_id=settings.s3.key,
        aws_secret_access_key=settings.s3.secret,
    ) as s3:
        bucket = await s3.Bucket(settings.s3.bucket)

        await bucket.upload_fileobj(file.file, "test/test_5.jpg")

    return {}
