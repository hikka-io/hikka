from app.models import Magazine
from sqlalchemy import select
from app import utils


async def save_magazines(session, data):
    content_ids = [entry["content_id"] for entry in data]

    cache = await session.scalars(
        select(Magazine).filter(Magazine.content_id.in_(content_ids))
    )

    magazines_cache = {entry.content_id: entry for entry in cache}

    add_magazines = []

    for magazine_data in data:
        slug = utils.slugify(magazine_data["name"], magazine_data["content_id"])

        if magazine_data["content_id"] not in magazines_cache:
            magazine = Magazine(
                **{
                    "content_id": magazine_data["content_id"],
                    "mal_id": magazine_data["mal_id"],
                    "name_en": magazine_data["name"],
                    "slug": slug,
                }
            )

            add_magazines.append(magazine)

            print(f"Added magazine: {magazine.name_en}")

    session.add_all(add_magazines)
    await session.commit()
