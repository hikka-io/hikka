from app.database import sessionmanager
from app.sync import update_aggregator
from app.utils import get_settings
import asyncio


async def import_aggregator():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    await update_aggregator()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(import_aggregator())
