from app.models import Anime, AnimeStaff
from app.sync.aggregator.info import update_anime_info
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from sqlalchemy import make_url, func
from sqlalchemy import select, desc
from app.utils import get_settings
from app.sync import sitemap
from app.sync import email
import asyncio


async def recalculate_anime_staff_weights():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        count = await session.scalar(
            select(func.count(AnimeStaff.id)).filter(
                AnimeStaff.weight == None  # noqa: E711
            )
        )

        while count > 0:
            print(count)

            staff_roles = await session.scalars(
                select(AnimeStaff)
                .options(selectinload(AnimeStaff.roles))
                .limit(20000)
            )

            for staff in staff_roles:
                staff.weight = sum([role.weight for role in staff.roles])
                session.add(staff)

            await session.commit()

            count = await session.scalar(
                select(func.count(AnimeStaff.id)).filter(
                    AnimeStaff.weight == None  # noqa: E711
                )
            )

    await sessionmanager.close()


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
    # asyncio.run(test_sitemap())
    # asyncio.run(test_check())
    # asyncio.run(import_role_weights())
    asyncio.run(recalculate_anime_staff_weights())
    # asyncio.run(test())
