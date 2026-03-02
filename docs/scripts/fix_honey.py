from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select
from app.models import Manga
import asyncio


async def fix_honey():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        manga = await session.scalars(
            select(Manga).filter(
                Manga.external.op("@>")([{"text": "Honey Manga"}]),
                Manga.needs_update == False,  # noqa: E712
            )
        )

        for entry in manga:
            entry.needs_update = True
            print(f"Requested info update for {entry.title_en}")

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_honey())
