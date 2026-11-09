from sqlalchemy.ext.asyncio import AsyncSession
from app.database import sessionmanager
from sqlalchemy import select, asc
from datetime import datetime
from app import constants

from app.utils import (
    utcfromtimestamp,
    utcnow,
)

from app.models import (
    SystemTimestamp,
    AnimeSchedule,
    Anime,
    Edit,
    Log,
)


async def update_schedule_aired(session: AsyncSession):
    now = utcnow()

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
            select(Anime).filter(
                Anime.id == schedule.anime_id,
                Anime.deleted == False,  # noqa: E712
            )
        )

        # Just in case
        if not anime:
            continue

        before = {}
        after = {}

        # Anilist bad schedule fix
        if (
            anime.episodes_total is not None
            and schedule.episode > anime.episodes_total
        ):
            continue

        # Update episodes released for anime
        if (
            not anime.episodes_released
            or schedule.episode > anime.episodes_released
        ):
            before["episodes_released"] = anime.episodes_released
            anime.episodes_released = schedule.episode
            after["episodes_released"] = anime.episodes_released

        # Change anime status when final episode has aired
        if (
            anime.episodes_total
            and schedule.episode == anime.episodes_total
            and anime.status != constants.RELEASE_STATUS_FINISHED
        ):
            before["status"] = anime.status
            anime.status = constants.RELEASE_STATUS_FINISHED
            after["status"] = anime.status

        # Set status to ongoing if anime just started airing
        if (
            anime.status == constants.RELEASE_STATUS_ANNOUNCED
            and anime.media_type != constants.MEDIA_TYPE_MOVIE
        ):
            before["status"] = anime.status
            anime.status = constants.RELEASE_STATUS_ONGOING
            after["status"] = anime.status

        # Only create new edit and log records when needed
        if before != {} and after != {}:
            # Status and episodes released are searchable
            # so search index has to be updated
            anime.needs_search_update = True

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

    # Fix for unupdated ongoing status
    # TODO: figure out why this is happening
    anime_list = await session.scalars(
        select(Anime)
        .filter(
            Anime.episodes_total > 1,
            Anime.episodes_released == Anime.episodes_total,
            Anime.status == constants.RELEASE_STATUS_ONGOING,
        )
        .order_by(Anime.id.desc())
    )

    for anime in anime_list:
        anime.status = constants.RELEASE_STATUS_FINISHED
        anime.needs_search_update = True

    await session.commit()


async def rollback_episodes_released(
    session: AsyncSession, episode: AnimeSchedule, anime: Anime
):
    # TODO: implement notification deletion logic for bad schedule (?)
    # TODO: implement anime status change (?)

    now = utcnow()

    # Stop if episode wasn't counted as released yet
    # or it has already aired (nothing to roll back)
    if (
        anime.episodes_released is None
        or anime.episodes_released < episode.episode
        or episode.airing_at < now
    ):
        return

    before = {}
    after = {}

    before["episodes_released"] = anime.episodes_released
    anime.episodes_released = episode.episode - 1
    after["episodes_released"] = anime.episodes_released

    # Episodes released is searchable so search index has to be updated
    anime.needs_search_update = True

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

        log_type = constants.LOG_SCHEDULE_ANIME_ROLLBACK
        log = Log(
            **{
                "target_id": anime.id,
                "log_type": log_type,
                "created": now,
                "user": None,
                "data": {
                    "before": before,
                    "after": after,
                },
            }
        )

        session.add_all([anime, edit, log])


async def build_schedule(session: AsyncSession):
    now = utcnow()

    statuses = [
        constants.RELEASE_STATUS_ANNOUNCED,
        constants.RELEASE_STATUS_ONGOING,
    ]

    anime_list = (
        await session.scalars(select(Anime).filter(Anime.status.in_(statuses)))
    ).all()

    cache = {}

    for entry in await session.scalars(
        select(AnimeSchedule)
        .join(AnimeSchedule.anime)
        .filter(Anime.status.in_(statuses))
    ):
        cache.setdefault(entry.anime_id, {})[entry.episode] = entry

    for anime in anime_list:
        episodes = cache.get(anime.id, {})

        if not anime.schedule and not episodes:
            continue

        scheduled = {}

        for episode_data in anime.schedule or []:
            # Sometimes Anilist returns more episodes than it should
            if (
                anime.episodes_total is not None
                and episode_data["episode"] > anime.episodes_total
            ):
                continue

            scheduled[episode_data["episode"]] = utcfromtimestamp(
                episode_data["airing_at"]
            )

        for number, airing_at in scheduled.items():
            if not (episode := episodes.get(number)):
                session.add(
                    AnimeSchedule(
                        **{
                            "episode": number,
                            "airing_at": airing_at,
                            "created": now,
                            "updated": now,
                            "anime": anime,
                        }
                    )
                )

                print(f"Added episode #{number} for {anime.title_ja}")

                continue

            if episode.airing_at == airing_at:
                continue

            episode.airing_at = airing_at
            episode.updated = now

            # Sometimes our schedule may be not up to date and system can
            # incorrectly set episodes_released for some entries
            # In this case we should roll it back
            await rollback_episodes_released(session, episode, anime)

            print(f"Updated episode #{number} for {anime.title_ja}")

        for number, episode in episodes.items():
            # Remove episodes above total and stale upcoming ones
            if (
                anime.episodes_total is not None
                and number > anime.episodes_total
            ) or (number not in scheduled and episode.airing_at > now):
                await session.delete(episode)

                print(f"Removed episode #{number} for {anime.title_ja}")

    await session.commit()


async def update_schedule_build():
    async with sessionmanager.session() as session:
        await build_schedule(session)


async def update_schedule():
    async with sessionmanager.session() as session:
        await update_schedule_aired(session)
