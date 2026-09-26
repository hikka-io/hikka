from app.models import Anime, Manga, Novel
from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import update
import asyncio


async def fix_needs_search():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        await session.execute(update(Anime).values(needs_update=True))
        await session.execute(update(Manga).values(needs_update=True))
        await session.execute(update(Novel).values(needs_update=True))

        await session.execute(update(Anime).values(needs_search_update=True))
        await session.execute(update(Manga).values(needs_search_update=True))
        await session.execute(update(Novel).values(needs_search_update=True))

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_template())
