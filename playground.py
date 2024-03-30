from app.utils import get_settings, calculate_collection_ranking
from app.sync.notifications import generate_notifications
from app.sync.aggregator.info import update_anime_info
from app.sync.ranking import recalculate_ranking_all
from app.service import calculate_watch_duration
from meilisearch_python_sdk import AsyncClient
from app.edit.utils import calculate_before
from sqlalchemy import select, desc, asc
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from sqlalchemy import make_url, func
from app.sync import update_search
from datetime import datetime
from app.sync import sitemap
from app.sync import email
from pprint import pprint
from app import constants
import asyncio
import math
import copy
import json

from app.sync.schedule import (
    update_schedule_aired,
    build_schedule,
)

from app.admin.service import (
    create_hikka_update_notification,
    delete_hikka_update_notification,
)

from app.models import (
    CommentVoteLegacy,
    AnimeStaffRole,
    AnimeSchedule,
    UserEditStats,
    CommentVote,
    AnimeStaff,
    AnimeWatch,
    Collection,
    Favourite,
    Comment,
    Anime,
    User,
    Edit,
    Log,
)


async def test_mass_notification():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        anime = await session.scalar(
            select(Anime).filter(Anime.slug == "sousou-no-frieren-ad4e3e")
        )

        user_ids = await session.scalars(
            select(AnimeWatch.user_id).filter(
                AnimeWatch.anime == anime,
                AnimeWatch.status.in_(
                    [constants.WATCH_PLANNED, constants.WATCH_WATCHING]
                ),
            )
        )

        print(user_ids.all())

    await sessionmanager.close()


async def test_sync_stuff():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        # await update_schedule_aired(session)
        # await build_schedule(session)
        # await generate_activity(session)
        # await recalculate_ranking_daily(session)
        await generate_notifications(session)
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


async def run_migrate_logs():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        comment_logs = await session.scalars(
            select(Log).filter(
                Log.log_type.in_(
                    [
                        constants.LOG_COMMENT_WRITE,
                        constants.LOG_COMMENT_EDIT,
                        constants.LOG_COMMENT_HIDE,
                    ]
                )
            )
        )

        for log in comment_logs:
            if "content_type" in log.data:
                continue

            comment = await session.scalar(
                select(Comment).filter(Comment.id == log.target_id)
            )

            log.data = copy.deepcopy(log.data)
            log.data["content_type"] = comment.content_type

            session.add(log)
            await session.commit()

            print(log.data)

    await sessionmanager.close()


async def spring_top():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        spring_result = await session.execute(
            select(Anime, func.count(Anime.id))
            .join(AnimeWatch, AnimeWatch.anime_id == Anime.id)
            .filter(AnimeWatch.status == constants.WATCH_PLANNED)
            .filter(Anime.year == 2024, Anime.season == constants.SEASON_SPRING)
            .group_by(Anime)
            .order_by(func.count(Anime.id).desc())
            .limit(10)
        )

        print("Spring 2024:")
        for anime, list_count in spring_result:
            print(
                list_count,
                f"https://hikka.io/anime/{anime.slug}",
            )

        winter_result = await session.execute(
            select(Anime, func.count(Anime.id))
            .join(AnimeWatch, AnimeWatch.anime_id == Anime.id)
            .filter(
                AnimeWatch.status.in_(
                    [
                        constants.WATCH_PLANNED,
                        constants.WATCH_WATCHING,
                        constants.WATCH_COMPLETED,
                    ]
                )
            )
            .filter(Anime.year == 2023, Anime.season == constants.SEASON_WINTER)
            .group_by(Anime)
            .order_by(func.count(Anime.id).desc())
            .limit(10)
        )

        print("Winter 2023:")
        for anime, list_count in winter_result:
            print(
                list_count,
                f"https://hikka.io/anime/{anime.slug}",
            )

    await sessionmanager.close()


async def test_build_schedule():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        now = datetime.utcnow()

        anime = await session.scalar(
            select(Anime).filter(Anime.slug == "kaijuu-8-gou-fefba2")
        )

        schedule = await session.scalars(
            select(AnimeSchedule).filter(AnimeSchedule.anime == anime)
        )

        cache = {entry.episode: entry for entry in schedule}

        for episode_data in anime.schedule:
            airing_at = datetime.utcfromtimestamp(episode_data["airing_at"])

            if not (episode := cache.get(episode_data["episode"])):
                episode = AnimeSchedule(
                    **{
                        "episode": episode_data["episode"],
                        "airing_at": airing_at,
                        "anime": anime,
                        "created": now,
                        "updated": now,
                    }
                )

                print(f"Added episode #{episode.episode} for {anime.title_ja}")

            if episode.airing_at != airing_at:
                episode.airing_at = airing_at
                episode.updated = now
                session.add(episode)

                print(
                    f"Updated episode #{episode.episode} for {anime.title_ja}"
                )

            session.add(episode)

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    # asyncio.run(test_email_template())
    # asyncio.run(test_sitemap())
    # asyncio.run(test_check())
    # asyncio.run(import_role_weights())
    # asyncio.run(recalculate_anime_staff_weights())
    # asyncio.run(query_activity())
    asyncio.run(test_sync_stuff())
    # asyncio.run(test_mass_notification())
    # asyncio.run(test_system_notification())
    # asyncio.run(run_search())
    # asyncio.run(watch_stats())
    # asyncio.run(fix_closed_edits())
    # asyncio.run(test())
    # asyncio.run(run_migrate_logs())
    # asyncio.run(calculate_stats())
    # asyncio.run(run_migrate_collections())
    # asyncio.run(run_migrate_votes())
    # asyncio.run(test_meiliserarch_ranking())
    # asyncio.run(spring_top())
    # asyncio.run(test_build_schedule())

    pass
