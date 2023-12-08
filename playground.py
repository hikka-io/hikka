from app.sync.aggregator.info import update_anime_info
from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select, desc
from sqlalchemy import make_url
from app.models import Anime
from app.sync import sitemap
from app.sync import email
import asyncio


async def test_sitemap():
    await sitemap.update_sitemap()


async def test_email_template():
    await email.send_emails()


async def test_check():
    settings = get_settings()
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")
    url = make_url(settings.database.endpoint)
    print(url.password)


async def test():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)
    semaphore = asyncio.Semaphore(10)

    async with sessionmanager.session() as session:
        anime = await session.scalar(
            select(Anime).order_by(desc("score"), desc("scored_by")).limit(1)
        )

        await update_anime_info(semaphore, anime.content_id)

    await sessionmanager.close()


if __name__ == "__main__":
    # asyncio.run(test_email_template())
    asyncio.run(test_sitemap())
    # asyncio.run(test_check())
    # asyncio.run(test())
