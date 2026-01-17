from app.sync.counts import update_counts
from app.database import sessionmanager
from app.utils import get_settings
import asyncio


async def fix_counts():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    await update_counts()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_counts())
