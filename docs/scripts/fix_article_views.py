from app.sync import update_article_views
from app.database import sessionmanager
from app.utils import get_settings
import asyncio


async def fix_article_views():
    settings = get_settings()
    sessionmanager.init(settings.database.endpoint)
    await update_article_views()
    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_article_views())
