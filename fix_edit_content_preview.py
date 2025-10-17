from app.database import sessionmanager
from sqlalchemy.orm import joinedload
from sqlalchemy import select, func
from app.utils import get_settings
from app.utils import pagination
from app import constants
import asyncio
import math

from app.models import (
    CharacterEdit,
    PersonEdit,
    AnimeEdit,
    MangaEdit,
    NovelEdit,
    Character,
    Person,
    Novel,
    Manga,
    Anime,
    Edit,
)


def generate_content_preview(edit: Edit) -> dict:
    match edit.content_type:
        case constants.CONTENT_ANIME:
            return {
                "title_ja": edit.content.title_ja,
                "title_en": edit.content.title_en,
                "title_ua": edit.content.title_ua,
                "slug": edit.content.slug,
            }

        case constants.CONTENT_MANGA | constants.CONTENT_NOVEL:
            return {
                "title_original": edit.content.title_original,
                "title_en": edit.content.title_en,
                "title_ua": edit.content.title_ua,
                "slug": edit.content.slug,
            }

        case constants.CONTENT_PERSON:
            return {
                "name_ja": edit.content.name_native,
                "name_en": edit.content.name_en,
                "name_ua": edit.content.name_ua,
                "slug": edit.content.slug,
            }

        case constants.CONTENT_CHARACTER:
            return {
                "name_ja": edit.content.name_ja,
                "name_en": edit.content.name_en,
                "name_ua": edit.content.name_ua,
                "slug": edit.content.slug,
            }

        case _:
            return {}


async def fix_edit_content_preview():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        total = await session.scalar(
            select(func.count(Edit.id)).filter(Edit.content_preview == {})
        )

        size = 1000

        pages = math.ceil(total / size)

        for page in range(1, pages + 1):
            limit, offset = pagination(page, size)

            query = (
                select(Edit)
                .order_by(Edit.edit_id.asc())
                .filter(Edit.content_preview == {})
                .limit(limit)
                .offset(offset)
            )

            query = query.options(
                joinedload(AnimeEdit.content).load_only(
                    Anime.title_ja,
                    Anime.title_en,
                    Anime.title_ua,
                    Anime.slug,
                ),
                joinedload(MangaEdit.content).load_only(
                    Manga.title_original,
                    Manga.title_en,
                    Manga.title_ua,
                    Manga.slug,
                ),
                joinedload(NovelEdit.content).load_only(
                    Novel.title_original,
                    Novel.title_en,
                    Novel.title_ua,
                    Novel.slug,
                ),
                joinedload(PersonEdit.content).load_only(
                    Person.name_native,
                    Person.name_en,
                    Person.name_ua,
                    Person.slug,
                ),
                joinedload(CharacterEdit.content).load_only(
                    Character.name_ja,
                    Character.name_en,
                    Character.name_ua,
                    Character.slug,
                ),
            )

            edits = await session.scalars(query)

            for edit in edits:
                edit.content_preview = generate_content_preview(edit)
                print(
                    f"Updated preview for {edit.content_type} {edit.content.slug}"
                )

            await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_edit_content_preview())
