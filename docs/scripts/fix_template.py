from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select
from app.models import Anime
import asyncio


async def fix_collection_comments():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        await session.scalar(select(Anime).limit(1))

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_collection_comments())
