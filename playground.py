from app.sync.notifications import generate_notifications
from app.sync.aggregator.info import update_anime_info
from app.service import calculate_watch_duration
from app.sync.activity import generate_activity
from app.edit.utils import calculate_before
from sqlalchemy import select, desc, asc
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from sqlalchemy import make_url, func
from app.utils import get_settings
from app.sync import update_search
from app.sync import sitemap
from app.sync import email
from app import constants
import asyncio
import math
import json

from app.admin.service import (
    create_hikka_update_notification,
    delete_hikka_update_notification,
)

from app.models import (
    AnimeStaffRole,
    AnimeStaff,
    AnimeWatch,
    Anime,
    Edit,
)


async def query_activity():
    from datetime import datetime, timedelta
    from app.models import Activity

    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        threshold = datetime.utcnow() - timedelta(days=1)

        test = await session.scalar(
            select(Activity).filter(Activity.created > threshold)
        )

        print(test)

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


async def watch_stats():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        watch_entries = await session.scalars(
            select(AnimeWatch)
            .options(selectinload(AnimeWatch.anime))
            .filter(AnimeWatch.duration == 0)
            .limit(20000)
        )

        for watch in watch_entries:
            watch.duration = calculate_watch_duration(watch)
            session.add(watch)
            await session.commit()

    await sessionmanager.close()


async def fix_closed_edits():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        edits = await session.scalars(
            select(Edit).filter(Edit.before == None)  # noqa: E711
        )

        for edit in edits:
            edit.before = calculate_before(edit.content, edit.after)
            session.add(edit)

        await session.commit()

    await sessionmanager.close()


async def test_sync_stuff():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        await generate_activity(session)
        # await generate_notifications(session)
        # await generate_history(session)

    await sessionmanager.close()


async def test_system_notification():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        update_name = "hikka_profile_update"

        await create_hikka_update_notification(
            session,
            update_name,
            "Розказуємо про основні зміни за останні кілька тижнів",
            "Редизайн профілю, активність та сповіщення",
            "https://t.me/hikka_io/10",
        )

        # await delete_hikka_update_notification(session, update_name)

    await sessionmanager.close()


async def run_search():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    await update_search()

    await sessionmanager.close()


if __name__ == "__main__":
    # asyncio.run(test_email_template())
    # asyncio.run(test_sitemap())
    # asyncio.run(test_check())
    # asyncio.run(import_role_weights())
    # asyncio.run(recalculate_anime_staff_weights())
    # asyncio.run(query_activity())
    # asyncio.run(test_sync_stuff())
    # asyncio.run(test_system_notification())
    asyncio.run(run_search())
    # asyncio.run(watch_stats())
    # asyncio.run(fix_closed_edits())
    # asyncio.run(test())
