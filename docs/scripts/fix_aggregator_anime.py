from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import update
from app.models import Anime
import asyncio


async def fix_aggregator_anime():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        await session.execute(update(Anime).values(needs_update=True))

        await session.commit()

        print("Reset aggregator anime update list")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_aggregator_anime())
