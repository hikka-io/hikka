from app.database import sessionmanager
from app.models import Person
from sqlalchemy import select
from . import requests
from app import utils
import asyncio
import config


async def make_request(semaphore, page):
    async with semaphore:
        data = await requests.get_people(page)
        return data["list"]


async def save_people(data):
    sessionmanager.init(config.database)

    async with sessionmanager.session() as session:
        references = [entry["reference"] for entry in data]

        cache = await session.scalars(
            select(Person).where(Person.content_id.in_(references))
        )

        people_cache = {entry.content_id: entry for entry in cache}

        add_people = []

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

                add_people.append(person)

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

                add_people.append(person)

                print(f"Added person: {person.name_en} ({person.favorites})")

        session.add_all(add_people)
        await session.commit()


async def aggregator_people():
    data = await requests.get_people(1)
    pages = data["pagination"]["pages"]

    semaphore = asyncio.Semaphore(20)
    tasks = [make_request(semaphore, page) for page in range(1, pages + 1)]

    result = await asyncio.gather(*tasks)

    data = [item for sublist in result for item in sublist]

    for data_chunk in utils.chunkify(data, 20000):
        await save_people(data_chunk)
