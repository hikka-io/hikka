from app.models import Character, Person, Anime, Manga, Novel, Image
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import chunkify, utcnow
from sqlalchemy import select, update


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


async def get_image_cache(session: AsyncSession, paths: list[str]):
    cache = await session.scalars(select(Image).filter(Image.path.in_(paths)))

    return {entry.path: entry for entry in cache}


def new_system_image(path: str) -> Image:
    return Image(
        **{
            "path": path,
            "created": utcnow(),
            "uploaded": True,
            "ignore": False,
            "system": True,
        }
    )


async def process_image(
    session: AsyncSession, content: Anime | Manga | Novel, data: dict
):
    if not data.get("poster"):
        return

    if "image" in content.ignored_fields:
        return

    if not (
        image := await session.scalar(
            select(Image).filter(Image.path == data["poster"])
        )
    ):
        image = new_system_image(data["poster"])

    session.add(image)
    content.image_relation = image
