from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Character
from app.utils import chunkify
from sqlalchemy import select


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
