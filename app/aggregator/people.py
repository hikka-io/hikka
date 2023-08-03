from app.models import Person, Image
from sqlalchemy import select
from datetime import datetime
from app import utils


async def save_people(session, data):
    content_ids = [entry["content_id"] for entry in data]
    images = [entry["image"] for entry in data]

    cache = await session.scalars(
        select(Person).where(Person.content_id.in_(content_ids))
    )

    people_cache = {entry.content_id: entry for entry in cache}

    cache = await session.scalars(select(Image).where(Image.path.in_(images)))

    image_cache = {entry.path: entry for entry in cache}

    add_people = []

    for person_data in data:
        updated = utils.from_timestamp(person_data["updated"])
        slug = utils.slugify(person_data["name_en"], person_data["content_id"])

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
