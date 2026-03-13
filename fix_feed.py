from app.database import sessionmanager
from app.utils import get_settings
from app.sync import generate_feed
import asyncio


async def fix_feed():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    await generate_feed()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_feed())
