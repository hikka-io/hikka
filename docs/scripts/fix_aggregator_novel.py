from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import update
from app.models import Novel
import asyncio


async def fix_aggregator_novel():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        await session.execute(update(Novel).values(needs_update=True))

        await session.commit()

        print("Reset aggregator novel update list")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_aggregator_novel())
