from app.models import Anime, Manga, Novel, Franchise
from app.database import sessionmanager
from sqlalchemy import update, delete
from app import utils
import asyncio


async def fix_reset_franchises():
    settings = utils.get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        await session.execute(update(Anime).values(franchise_id=None))
        await session.execute(update(Manga).values(franchise_id=None))
        await session.execute(update(Novel).values(franchise_id=None))
        await session.execute(delete(Franchise))
        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_reset_franchises())
