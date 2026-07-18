from app.sync.digests.user_stats import digest_user_stats
from app.database import sessionmanager
from app.utils import get_settings
import asyncio


async def fix_user_stats():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    await digest_user_stats()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_user_stats())
