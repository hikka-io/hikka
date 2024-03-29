from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Anime, AnimeSchedule
from datetime import datetime
from sqlalchemy import select
from app import constants


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


async def update_schedule_aired(session: AsyncSession):
    now = datetime.utcnow()
