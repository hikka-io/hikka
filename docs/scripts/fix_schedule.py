from app.utils import get_airing_seasons
from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select
from app.models import Anime
from app import constants
import asyncio


async def fix_airing_seasons():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        anime_list = await session.scalars(
            select(Anime)
            .filter(
                Anime.airing_seasons == [],
                Anime.start_date != None,  # noqa: E711
                # Anime.end_date != None,  # noqa: E711
            )
            .order_by(Anime.id.desc())
        )

        for anime in anime_list:
            anime.needs_search_update = True
            anime.airing_seasons = get_airing_seasons(
                anime.start_date, anime.end_date
            )

            print(f"{anime.title_ua}, {anime.airing_seasons}")

        await session.commit()

    await sessionmanager.close()


async def fix_episodes_overflow():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        anime_list = await session.scalars(
            select(Anime)
            .filter(Anime.episodes_released > Anime.episodes_total)
            .order_by(Anime.id.desc())
        )

        for anime in anime_list:
            anime.episodes_released = anime.episodes_total
            print(f"{anime.title_ua}")

        await session.commit()

    await sessionmanager.close()


async def fix_unupdated_ongoing():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
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
            print(f"{anime.title_ua}")

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_airing_seasons())
    asyncio.run(fix_episodes_overflow())
    asyncio.run(fix_unupdated_ongoing())
