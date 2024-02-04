from app.models import Anime, AnimeStaffRole, AnimeStaff
from app.sync.aggregator.info import update_anime_info
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from sqlalchemy import make_url, func
from sqlalchemy import select, desc
from app.utils import get_settings
from app.sync import sitemap
from app.sync import email
import asyncio
import math
import json


async def query_watari():
    from app.models import Anime
    from sqlalchemy import select
    from sqlalchemy import lateral
    from sqlalchemy.orm import aliased

    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        # subquery = (
        #     select(Anime.id)
        #     .filter(
        #         func.jsonb_array_elements_text(Anime.external).contains(
        #             {
        #                 "url": "https://watari-anime.com/watch?wid=f547da6a-7dd3-43cd-95d3-05a9f9bcd70d"
        #             }
        #         )
        #     )
        #     .limit(1)
        #     .subquery()
        # )

        test_anime = await session.scalar(
            select(Anime).filter(
                Anime.external.op("@>")(
                    [
                        {
                            # "url": "https://watari-anime.com/watch?wid=f547da6a-7dd3-43cd-95d3-05a9f9bcd70d"
                        }
                    ]
                )
            )
        )

        # test_anime = await session.scalar(
        #     select(Anime).filter(
        #         func.jsonb_array_elements_text(Anime.external).contains(
        #             {
        #                 "url": "https://watari-anime.com/watch?wid=f547da6a-7dd3-43cd-95d3-05a9f9bcd70d"
        #             }
        #         )
        #     )
        # )

        print(test_anime.title_ja)

    await sessionmanager.close()


async def import_role_weights():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        with open("docs/roles.json", "r") as file:
            data = json.load(file)

            for entry in data["service_content_anime_staff_roles"]:
                role = await session.scalar(
                    select(AnimeStaffRole).filter(
                        AnimeStaffRole.slug == entry["slug"]
                    )
                )

                role.name_ua = entry["name_ua"]
                role.weight = entry["weight"]

                session.add(role)

            await session.commit()

    await sessionmanager.close()


async def recalculate_anime_staff_weights():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        limit = 10000
        total = await session.scalar(select(func.count(AnimeStaff.id)))
        pages = math.ceil(total / limit) + 1

        for page in range(1, pages):
            print(page)

            offset = (limit * (page)) - limit

            staff_roles = await session.scalars(
                select(AnimeStaff)
                .options(selectinload(AnimeStaff.roles))
                .order_by(desc(AnimeStaff.id))
                .limit(limit)
                .offset(offset)
            )

            for staff in staff_roles:
                staff.weight = sum([role.weight for role in staff.roles])
                session.add(staff)

            await session.commit()

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
    # asyncio.run(recalculate_anime_staff_weights())
    asyncio.run(query_watari())
    # asyncio.run(test())
