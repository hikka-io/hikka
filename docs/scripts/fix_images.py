from app.utils import get_settings, chunkify
from app.models import Image, Upload, Log
from app.database import sessionmanager
from sqlalchemy import select
from app import constants
import asyncio


async def fix_images():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        images = await session.scalars(
            select(Image).filter(
                Image.system == False,  # noqa: E712
                Image.type == None,  # noqa: E711
            )
        )

        images = images.all()

        for images_chunk in chunkify(images, 10000):
            uploads = await session.scalars(
                select(Upload).filter(
                    Upload.path.in_([image.path for image in images_chunk])
                )
            )

            uploads_cache = {upload.path: upload for upload in uploads}

            for image in images:
                upload = uploads_cache.get(image.path)

                if not upload:
                    if "/uploads/" in image.path:
                        print(image.path)
                        continue

                    image.system = True

                    print(f"Marked image {image.path} as system")

                else:
                    image.mime_type = upload.mime_type
                    image.user_id = upload.user_id
                    image.size = upload.size
                    image.type = upload.type
                    image.system = False

                    print(f"Updated image {image.path} with upload details")

            await session.commit()

        logs = await session.scalars(
            select(Log).filter(Log.log_type == constants.LOG_UPLOAD)
        )

        logs = logs.all()

        uploads = await session.scalars(
            select(Upload).filter(
                Upload.id.in_([log.target_id for log in logs])
            )
        )

        uploads = uploads.all()
        uploads_cache = {upload.id: upload for upload in uploads}

        images = await session.scalars(
            select(Image).filter(
                Image.path.in_([upload.path for upload in uploads])
            )
        )

        images_cache = {image.path: image for image in images}

        for log in logs:
            if not (upload := uploads_cache.get(log.target_id)):
                continue

            if not (image := images_cache.get(upload.path)):
                continue

            log.target_id = image.id

            print(f"Updated upload log {log.reference}")

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_images())
