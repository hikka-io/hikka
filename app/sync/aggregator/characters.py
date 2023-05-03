from app.models import Character
from tortoise import Tortoise
from app import utils
from . import requests
import asyncio
import config


async def make_request(semaphore, page):
    async with semaphore:
        data = await requests.get_characters(page)
        return data["list"]


async def save_characters(data):
    references = [entry["reference"] for entry in data]

    cache = await Character.filter(content_id__in=references)

    characters_cache = {entry.content_id: entry for entry in cache}

    create_characters = []
    update_characters = []

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

            await character.save()

            update_characters.append(character)

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

            create_characters.append(character)

            print(
                f"Added character: {character.name_en} ({character.favorites})"
            )

    await Character.bulk_create(create_characters)

    if len(update_characters) > 0:
        await Character.bulk_update(
            update_characters, fields=["updated", "favorites"]
        )


async def aggregator_characters():
    await Tortoise.init(config=config.tortoise)
    await Tortoise.generate_schemas()

    data = await requests.get_characters(1)
    pages = data["pagination"]["pages"]

    semaphore = asyncio.Semaphore(20)
    tasks = [make_request(semaphore, page) for page in range(1, pages + 1)]

    result = await asyncio.gather(*tasks)

    data = [item for sublist in result for item in sublist]

    await save_characters(data)
