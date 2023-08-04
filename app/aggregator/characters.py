from app.models import Character, Image
from sqlalchemy import select
from datetime import datetime
from app import utils


async def save_characters(session, data):
    content_ids = [entry["content_id"] for entry in data]
    images = [entry["image"] for entry in data]

    cache = await session.scalars(
        select(Character).where(Character.content_id.in_(content_ids))
    )

    characters_cache = {entry.content_id: entry for entry in cache}

    cache = await session.scalars(select(Image).where(Image.path.in_(images)))

    image_cache = {entry.path: entry for entry in cache}

    add_characters = []

    for character_data in data:
        updated = utils.from_timestamp(character_data["updated"])
        slug = utils.slugify(
            character_data["name_en"], character_data["content_id"]
        )

        if character_data["content_id"] in characters_cache:
            character = characters_cache[character_data["content_id"]]

            if character.updated == updated:
                continue

            if character.favorites == character_data["favorites"]:
                continue

            character.favorites = character_data["favorites"]
            character.updated = updated

            add_characters.append(character)

            print(
                f"Updated character: {character.name_en} ({character.favorites})"  # noqa: E501
            )

        else:
            if not (image := image_cache.get(character_data["image"])):
                if character_data["image"]:
                    image = Image(
                        **{
                            "path": character_data["image"],
                            "created": datetime.utcnow(),
                            "uploaded": True,
                            "ignore": False,
                        }
                    )

                    image_cache[character_data["image"]] = image

            character = Character(
                **{
                    "content_id": character_data["content_id"],
                    "favorites": character_data["favorites"],
                    "name_ja": character_data["name_ja"],
                    "name_en": character_data["name_en"],
                    "image_relation": image,
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
