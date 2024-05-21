from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select
from app.models import Anime
import asyncio


async def fix_watari():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        anime_list = await session.scalars(
            select(Anime).filter(
                Anime.external.op("@>")([{"text": "Watari Anime"}])
            )
        )

        for anime in anime_list:
            if anime.needs_update:
                continue

            anime.needs_update = True
            session.add(anime)

            print(f"Requested update for anime {anime.title_ua}")

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_watari())
