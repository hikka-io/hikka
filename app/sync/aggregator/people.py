from app.models import Person
from tortoise import Tortoise
from app import utils
from . import requests
import asyncio
import config


async def make_request(semaphore, page):
    async with semaphore:
        data = await requests.get_people(page)
        return data["list"]


async def save_people(data):
    references = [entry["reference"] for entry in data]

    cache = await Person.filter(content_id__in=references)

    people_cache = {entry.content_id: entry for entry in cache}

    create_people = []
    update_people = []

    for person_data in data:
        updated = utils.from_timestamp(person_data["updated"])
        slug = utils.slugify(person_data["name"], person_data["reference"])

        if person_data["reference"] in people_cache:
            person = people_cache[person_data["reference"]]

            if person.updated == updated:
                continue

            if person.favorites == person_data["favorites"]:
                continue

            person.favorites = person_data["favorites"]
            person.updated = updated

            await person.save()

            update_people.append(person)

            print(f"Updated person: {person.name_en} ({person.favorites})")

        else:
            person = Person(
                **{
                    "content_id": person_data["reference"],
                    "name_native": person_data["name_ja"],
                    "favorites": person_data["favorites"],
                    "name_en": person_data["name"],
                    "updated": updated,
                    "slug": slug,
                }
            )

            create_people.append(person)

            print(f"Added person: {person.name_en} ({person.favorites})")

    await Person.bulk_create(create_people)

    if len(update_people) > 0:
        await Person.bulk_update(update_people, fields=["updated", "favorites"])


async def aggregator_people():
    await Tortoise.init(config=config.tortoise)
    await Tortoise.generate_schemas()

    data = await requests.get_people(1)
    pages = data["pagination"]["pages"]

    semaphore = asyncio.Semaphore(20)
    tasks = [make_request(semaphore, page) for page in range(1, pages + 1)]

    result = await asyncio.gather(*tasks)

    data = [item for sublist in result for item in sublist]

    await save_people(data)
