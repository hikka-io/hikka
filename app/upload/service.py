from datetime import datetime, timedelta
from app.utils import get_settings
from app.utils import new_token
from fastapi import UploadFile
from uuid import uuid4
from . import utils
import aioboto3


# async def create_upload_request(
#     user: User, args: UploadRequestArgs
# ) -> UploadFile:
#     # user = User(
#     #     **{
#     #         "role": constants.ROLE_NOT_ACTIVATED,
#     #         "activation_expire": now + timedelta(hours=3),
#     #         "activation_token": activation_token,
#     #         "password_hash": password_hash,
#     #         "username": signup.username,
#     #         "email": signup.email,
#     #         "last_active": now,
#     #         "created": now,
#     #         "login": now,
#     #     }
#     # )

#     # session.add(user)
#     # await session.commit()

#     now = datetime.utcnow()

#     extension = utils.get_mime_extension(args.mime_type)

#     file_path = (
#         f"uploads/{user.username}/{args.type}/{str(uuid4())}.{extension}"
#     )

#     request = UploadRequest(
#         **{
#             "expiration": now + timedelta(minutes=3),
#             "mime_type": args.mime_type,
#             "secret": new_token(),
#             "type": args.type,
#             "path": file_path,
#             "size": args.size,
#             "created": now,
#             "user": user,
#         }
#     )

#     return request


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
