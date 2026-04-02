from app.database import sessionmanager
from app.utils import get_settings
from app.sync import update_search
import asyncio


async def fix_collection_comments():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    await update_search()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_collection_comments())
