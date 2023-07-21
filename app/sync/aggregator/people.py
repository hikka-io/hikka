from app.database import sessionmanager
from app.models import Person, Image
from sqlalchemy import select
from datetime import datetime
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
        content_ids = [entry["content_id"] for entry in data]
        images = [entry["image"] for entry in data]

        cache = await session.scalars(
            select(Person).where(Person.content_id.in_(content_ids))
        )

        people_cache = {entry.content_id: entry for entry in cache}

        cache = await session.scalars(
            select(Image).where(Image.path.in_(images))
        )

        image_cache = {entry.path: entry for entry in cache}

        add_people = []

        for person_data in data:
            updated = utils.from_timestamp(person_data["updated"])
            slug = utils.slugify(
                person_data["name_en"], person_data["content_id"]
            )

            if person_data["content_id"] in people_cache:
                person = people_cache[person_data["content_id"]]

                if person.updated == updated:
                    continue

                if person.favorites == person_data["favorites"]:
                    continue

                person.favorites = person_data["favorites"]
                person.updated = updated

                add_people.append(person)

                print(f"Updated person: {person.name_en} ({person.favorites})")

            else:
                if not (image := image_cache.get(person_data["image"])):
                    if person_data["image"]:
                        image = Image(
                            **{
                                "path": person_data["image"],
                                "created": datetime.utcnow(),
                                "uploaded": True,
                                "ignore": False,
                            }
                        )

                        image_cache[person_data["image"]] = image

                person = Person(
                    **{
                        "content_id": person_data["content_id"],
                        "name_native": person_data["name_ja"],
                        "favorites": person_data["favorites"],
                        "name_en": person_data["name_en"],
                        "image_relation": image,
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
