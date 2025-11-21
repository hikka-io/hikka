from app.models import Anime, Manga, Character, Person, Comment
from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select
import asyncio


async def fix_strip_descripion():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        anime = await session.scalars(select(Anime))

        for entry in anime:
            entry.synopsis_en = (
                entry.synopsis_en.strip()
                if entry.synopsis_en
                else entry.synopsis_en
            )
            entry.synopsis_ua = (
                entry.synopsis_ua.strip()
                if entry.synopsis_ua
                else entry.synopsis_ua
            )

            if session.is_modified(entry):
                print(f"Stripped anime {entry.title_ja}")

        await session.commit()

        manga = await session.scalars(select(Manga))

        for entry in manga:
            entry.synopsis_en = (
                entry.synopsis_en.strip()
                if entry.synopsis_en
                else entry.synopsis_en
            )
            entry.synopsis_ua = (
                entry.synopsis_ua.strip()
                if entry.synopsis_ua
                else entry.synopsis_ua
            )

            if session.is_modified(entry):
                print(f"Stripped manga {entry.title_original}")

        await session.commit()

        characters = await session.scalars(select(Character))

        for entry in characters:
            entry.description_ua = (
                entry.description_ua.strip()
                if entry.description_ua
                else entry.description_ua
            )

            if session.is_modified(entry):
                print(f"Stripped character {entry.name_ja}")

        await session.commit()

        people = await session.scalars(select(Person))

        for entry in people:
            entry.description_ua = (
                entry.description_ua.strip()
                if entry.description_ua
                else entry.description_ua
            )

            if session.is_modified(entry):
                print(f"Stripped person {entry.name_native}")

        await session.commit()

        comments = await session.scalars(select(Comment))

        for entry in comments:
            entry.text = entry.text.strip()

            if session.is_modified(entry):
                print(f"Stripped comment {entry.reference}")

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_strip_descripion())
