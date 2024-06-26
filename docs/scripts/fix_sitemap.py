from app.sync.sitemap import update_sitemap
from app.database import sessionmanager
from app.utils import get_settings
import asyncio


async def fix_sitemap():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    await update_sitemap()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_sitemap())
