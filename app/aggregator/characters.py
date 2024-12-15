from app.models import Character, Image
from sqlalchemy import select
from app.utils import utcnow
from app import utils


async def save_characters(session, data):
    content_ids = [entry["content_id"] for entry in data]
    images = [entry["image"] for entry in data]

    cache = await session.scalars(
        select(Character).filter(Character.content_id.in_(content_ids))
    )

    characters_cache = {entry.content_id: entry for entry in cache}

    cache = await session.scalars(select(Image).filter(Image.path.in_(images)))

    image_cache = {entry.path: entry for entry in cache}

    add_characters = []

    for character_data in data:
        new_image = False

        if not (image := image_cache.get(character_data["image"])):
            if character_data["image"]:
                image = Image(
                    **{
                        "path": character_data["image"],
                        "created": utcnow(),
                        "uploaded": True,
                        "ignore": False,
                    }
                )

                image_cache[character_data["image"]] = image
                new_image = True

        updated = utils.from_timestamp(character_data["updated"])
        slug = utils.slugify(
            character_data["name_en"], character_data["content_id"]
        )

        if character_data["content_id"] in characters_cache:
            character = characters_cache[character_data["content_id"]]

            # We only skip if there is nothing to update
            if all(
                [
                    character.updated == updated,
                    character.favorites == character_data["favorites"],
                    new_image is False,
                ]
            ):
                continue

            character.favorites = character_data["favorites"]
            character.image_relation = image
            character.updated = updated

            add_characters.append(character)

            # print(
            #     f"Updated character: {character.name_en} ({character.favorites})"  # noqa: E501
            # )

        else:
            character = Character(
                **{
                    "needs_search_update": True,
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

            # print(
            #     f"Added character: {character.name_en} ({character.favorites})"
            # )

    session.add_all(add_characters)
    await session.commit()
