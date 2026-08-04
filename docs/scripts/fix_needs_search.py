from app.database import sessionmanager
from app.models import Anime, Manga
from app.utils import get_settings
from sqlalchemy import update
import asyncio


async def fix_template():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        # await session.execute(update(Anime).values(needs_update=True))
        await session.execute(update(Manga).values(needs_search_update=True))
        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_template())
