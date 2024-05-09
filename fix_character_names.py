from app.utils import get_settings, utcnow
from app.database import sessionmanager
from app.models import Edit, Character
from sqlalchemy import select
from app import constants
import asyncio


def fix_name(raw_name):
    name = raw_name.split(", ")
    name.reverse()
    name = [element.strip() for element in name]
    return " ".join(name)


async def fix_character_names():
    # Context: at some point aggregator stopped processing character names
    # properly. This script fixes them, creates corresponding edit and
    # marks characters for Meilisearch update.

    settings = get_settings()
    now = utcnow()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        characters_list = await session.scalars(
            select(Character).filter(Character.name_en.contains(", "))
        )

        for character in characters_list:
            before = {"name_en": character.name_en}

            character.name_en = fix_name(character.name_en)
            character.needs_search_update = True

            after = {"name_en": character.name_en}

            edit = Edit(
                **{
                    "content_type": constants.CONTENT_CHARACTER,
                    "status": constants.EDIT_ACCEPTED,
                    "content_id": character.reference,
                    "system_edit": True,
                    "before": before,
                    "after": after,
                    "created": now,
                    "updated": now,
                }
            )

            print(f"Fixed character's {character.name_en} name")

            session.add_all([character, edit])
            await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_character_names())
