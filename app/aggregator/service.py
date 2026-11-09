from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Character, Person
from sqlalchemy import select, update
from app.utils import chunkify


async def get_characters_cache(
    session: AsyncSession, character_content_ids: list[str]
):
    characters_cache = {}

    for character_content_ids_batch in chunkify(character_content_ids, 1000):
        cache = await session.scalars(
            select(Character).filter(
                Character.content_id.in_(character_content_ids_batch)
            )
        )

        characters_cache |= {entry.content_id: entry for entry in cache}

    return characters_cache


async def mark_count_update(
    session: AsyncSession, model: type[Character] | type[Person], ids: set
):
    # Counts are only recalculated for flagged rows
    if not ids:
        return

    await session.execute(
        update(model)
        .filter(model.id.in_(list(ids)))
        .values(needs_count_update=True)
    )
