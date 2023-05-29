from app.database import sessionmanager
from app.models import Character
from sqlalchemy import select
from . import requests
from app import utils
import asyncio
import config

from sqlalchemy.exc import InterfaceError


async def make_request(semaphore, page):
    async with semaphore:
        data = await requests.get_characters(page)
        return data["list"]


async def save_characters(data):
    sessionmanager.init(config.database)

    async with sessionmanager.session() as session:
        references = [entry["reference"] for entry in data]

        cache = await session.scalars(
            select(Character).where(Character.content_id.in_(references))
        )

        characters_cache = {entry.content_id: entry for entry in cache}

        add_characters = []

        for character_data in data:
            updated = utils.from_timestamp(character_data["updated"])
            slug = utils.slugify(
                character_data["name"], character_data["reference"]
            )

            if character_data["reference"] in characters_cache:
                character = characters_cache[character_data["reference"]]

                if character.updated == updated:
                    continue

                if character.favorites == character_data["favorites"]:
                    continue

                character.favorites = character_data["favorites"]
                character.updated = updated

                add_characters.append(character)

                print(
                    f"Updated character: {character.name_en} ({character.favorites})"
                )

            else:
                character = Character(
                    **{
                        "content_id": character_data["reference"],
                        "favorites": character_data["favorites"],
                        "name_ja": character_data["name_ja"],
                        "name_en": character_data["name"],
                        "updated": updated,
                        "slug": slug,
                    }
                )

                add_characters.append(character)

                print(
                    f"Added character: {character.name_en} ({character.favorites})"
                )

        session.add_all(add_characters)
        await session.commit()


async def aggregator_characters():
    data = await requests.get_characters(1)
    pages = data["pagination"]["pages"]

    semaphore = asyncio.Semaphore(20)
    tasks = [make_request(semaphore, page) for page in range(1, pages + 1)]

    result = await asyncio.gather(*tasks)

    data = [item for sublist in result for item in sublist]

    for data_chunk in utils.chunkify(data, 20000):
        await save_characters(data_chunk)
