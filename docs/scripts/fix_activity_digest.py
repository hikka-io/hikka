from app.database import sessionmanager
from app.sync import digest_activity
from app.utils import get_settings
import asyncio


async def fix_activity_digest():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    await digest_activity()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_activity_digest())
