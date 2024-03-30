from sqlalchemy.ext.asyncio import AsyncSession
from app.database import sessionmanager
from sqlalchemy import select, asc
from datetime import datetime
from app import constants
import copy

from app.models import (
    SystemTimestamp,
    AnimeSchedule,
    Anime,
    Edit,
    Log,
)


async def update_schedule_aired(session: AsyncSession):
    now = datetime.utcnow()

    # Get system timestamp for latest known aired episode
    if not (
        system_timestamp := await session.scalar(
            select(SystemTimestamp).filter(
                SystemTimestamp.name == "schedule_anime"
            )
        )
    ):
        system_timestamp = SystemTimestamp(
            **{
                "timestamp": datetime(2010, 1, 1),
                "name": "schedule_anime",
            }
        )

    aired = await session.scalars(
        select(AnimeSchedule)
        .filter(
            AnimeSchedule.airing_at > system_timestamp.timestamp,
            AnimeSchedule.airing_at <= now,
        )
        .order_by(asc(AnimeSchedule.airing_at))
    )

    for schedule in aired:
        system_timestamp.timestamp = schedule.airing_at

        anime = await session.scalar(
            select(Anime).filter(Anime.id == schedule.anime_id)
        )

        # Fix for SQLAlchemy shenanigans
        anime.ignored_fields = copy.deepcopy(anime.ignored_fields)

        before = {}
        after = {}

        # Update episodes released for anime
        if (
            not anime.episodes_released
            or schedule.episode > anime.episodes_released
        ):
            before["episodes_released"] = anime.episodes_released
            anime.episodes_released = schedule.episode
            after["episodes_released"] = anime.episodes_released

            if "episodes_released" not in anime.ignored_fields:
                anime.ignored_fields.append("episodes_released")

        # Change anime status when final episode has aired
        if (
            anime.episodes_total
            and schedule.episode == anime.episodes_total
            and anime.status != constants.RELEASE_STATUS_FINISHED
        ):
            before["status"] = anime.status
            anime.status = constants.RELEASE_STATUS_FINISHED
            after["status"] = anime.status

            if "status" not in anime.ignored_fields:
                anime.ignored_fields.append("status")

        # Set status to ongoing if anime just started airing
        if (
            schedule.episode == 1
            and anime.episodes_released == 0
            and anime.status == constants.RELEASE_STATUS_ANNOUNCED
            and anime.media_type != constants.MEDIA_TYPE_MOVIE
        ):
            before["status"] = anime.status
            anime.status = constants.RELEASE_STATUS_ONGOING
            after["status"] = anime.status

            if "status" not in anime.ignored_fields:
                anime.ignored_fields.append("status")

        # Only create new edit and log records when needed
        if before != {} and after != {}:
            edit = Edit(
                **{
                    "content_type": constants.CONTENT_ANIME,
                    "status": constants.EDIT_ACCEPTED,
                    "content_id": anime.reference,
                    "system_edit": True,
                    "before": before,
                    "after": after,
                    "created": now,
                    "updated": now,
                }
            )

            log = Log(
                **{
                    "log_type": constants.LOG_SCHEDULE_ANIME,
                    "target_id": anime.id,
                    "created": now,
                    "user": None,
                    "data": {
                        "before": before,
                        "after": after,
                    },
                }
            )

            session.add_all([anime, edit, log])
            await session.commit()

    session.add(system_timestamp)
    await session.commit()


async def build_schedule(session: AsyncSession):
    now = datetime.utcnow()

    anime_list = await session.scalars(
        select(Anime).filter(
            Anime.status.in_(
                [
                    constants.RELEASE_STATUS_ANNOUNCED,
                    constants.RELEASE_STATUS_ONGOING,
                ]
            )
        )
    )

    for anime in anime_list:
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
                        "created": now,
                        "updated": now,
                        "anime": anime,
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


async def update_schedule_build():
    async with sessionmanager.session() as session:
        await build_schedule(session)


async def update_schedule():
    async with sessionmanager.session() as session:
        await update_schedule_aired(session)
