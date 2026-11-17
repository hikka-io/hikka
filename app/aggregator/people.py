from app.aggregator import service
from app.models import Person
from sqlalchemy import select
from app import utils


async def save_people(session, data):
    content_ids = [entry["content_id"] for entry in data]
    images = [entry["image"] for entry in data]

    cache = await session.scalars(
        select(Person).filter(Person.content_id.in_(content_ids))
    )

    people_cache = {entry.content_id: entry for entry in cache}

    image_cache = await service.get_image_cache(session, images)

    add_people = []

    for person_data in data:
        new_image = False

        if not (image := image_cache.get(person_data["image"])):
            if person_data["image"]:
                image = service.new_system_image(person_data["image"])

                image_cache[person_data["image"]] = image
                new_image = True

        updated = utils.from_timestamp(person_data["updated"])
        slug = utils.slugify(person_data["name_en"], person_data["content_id"])

        if person_data["content_id"] in people_cache:
            person = people_cache[person_data["content_id"]]

            # We only skip if there is nothing to update
            if all(
                [
                    person.updated == updated,
                    person.favorites == person_data["favorites"],
                    new_image is False,
                ]
            ):
                continue

            person.favorites = person_data["favorites"]
            person.image_relation = image
            person.updated = updated

            add_people.append(person)

            # print(f"Updated person: {person.name_en} ({person.favorites})")

        else:
            person = Person(
                **{
                    "needs_search_update": True,
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

            # print(f"Added person: {person.name_en} ({person.favorites})")

    session.add_all(add_people)
    await session.commit()
