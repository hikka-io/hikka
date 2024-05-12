from app.models import Collection, CollectionComment
from app.database import sessionmanager
from sqlalchemy import select, update
from app.utils import get_settings
from app import constants
import asyncio


async def fix_collection_comments():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        collections = await session.scalars(
            select(Collection).filter(
                Collection.visibility == constants.COLLECTION_PRIVATE
            )
        )

        for collection in collections:
            await session.execute(
                update(CollectionComment)
                .filter(CollectionComment.content == collection)
                .values(private=True)
            )

            await session.commit()

            print(f"Hide comments for private collection {collection.title}")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_collection_comments())
