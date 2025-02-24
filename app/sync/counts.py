from app.database import sessionmanager
from sqlalchemy import select
from sqlalchemy import func

from app.models import (
    AnimeCharacter,
    MangaCharacter,
    NovelCharacter,
    AnimeVoice,
    Character,
    Anime,
    Manga,
    Novel,
)


async def update_counts():
    async with sessionmanager.session() as session:
        characters = await session.scalars(
            select(Character).filter(
                Character.needs_count_update == True,  # noqa: E712
            )
        )

        character_anime_counts = await session.execute(
            select(
                AnimeCharacter.character_id,
                func.count()
                .filter(Anime.deleted == False)  # noqa: E712
                .label("anime_count"),
            )
            .join(Anime)
            .join(Character, Character.id == AnimeCharacter.character_id)
            .filter(Character.needs_count_update == True)  # noqa: E712
            .group_by(AnimeCharacter.character_id)
        )

        character_manga_counts = await session.execute(
            select(
                MangaCharacter.character_id,
                func.count()
                .filter(Manga.deleted == False)  # noqa: E712
                .label("manga_count"),
            )
            .join(Manga)
            .join(Character, Character.id == MangaCharacter.character_id)
            .filter(Character.needs_count_update == True)  # noqa: E712
            .group_by(MangaCharacter.character_id)
        )

        character_novel_counts = await session.execute(
            select(
                NovelCharacter.character_id,
                func.count()
                .filter(Novel.deleted == False)  # noqa: E712
                .label("novel_count"),
            )
            .join(Novel)
            .join(Character, Character.id == NovelCharacter.character_id)
            .filter(Character.needs_count_update == True)  # noqa: E712
            .group_by(NovelCharacter.character_id)
        )

        character_voices_counts = await session.execute(
            select(
                AnimeVoice.character_id,
                func.count()
                .filter(Anime.deleted == False)  # noqa: E712
                .label("voices_count"),
            )
            .join(Anime)
            .join(Character, Character.id == AnimeVoice.character_id)
            .filter(Character.needs_count_update == True)  # noqa: E712
            .group_by(AnimeVoice.character_id)
        )

        character_anime_count_dict = {
            character_id: count
            for character_id, count in character_anime_counts
        }

        character_manga_count_dict = {
            character_id: count
            for character_id, count in character_manga_counts
        }

        character_novel_count_dict = {
            character_id: count
            for character_id, count in character_novel_counts
        }

        character_voices_count_dict = {
            character_id: count
            for character_id, count in character_voices_counts
        }

        for character in characters:
            character.anime_count = character_anime_count_dict.get(
                character.id, 0
            )

            character.manga_count = character_manga_count_dict.get(
                character.id, 0
            )

            character.novel_count = character_novel_count_dict.get(
                character.id, 0
            )

            character.voices_count = character_voices_count_dict.get(
                character.id, 0
            )

            character.needs_count_update = False

            print(
                f"Updated counts for character {character.name_en} ("
                f"{character.anime_count} / {character.manga_count} / "
                f"{character.novel_count} / {character.voices_count})"
            )

        await session.commit()
