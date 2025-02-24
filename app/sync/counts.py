from sqlalchemy.ext.asyncio import AsyncSession
from app.database import sessionmanager
from sqlalchemy import select
from sqlalchemy import func

from app.models import (
    AnimeCharacter,
    MangaCharacter,
    NovelCharacter,
    MangaAuthor,
    NovelAuthor,
    AnimeStaff,
    AnimeVoice,
    Character,
    Person,
    Anime,
    Manga,
    Novel,
)


async def character_count(session: AsyncSession):
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
        character_id: count for character_id, count in character_anime_counts
    }

    character_manga_count_dict = {
        character_id: count for character_id, count in character_manga_counts
    }

    character_novel_count_dict = {
        character_id: count for character_id, count in character_novel_counts
    }

    character_voices_count_dict = {
        character_id: count for character_id, count in character_voices_counts
    }

    for character in characters:
        character.anime_count = character_anime_count_dict.get(character.id, 0)

        character.manga_count = character_manga_count_dict.get(character.id, 0)

        character.novel_count = character_novel_count_dict.get(character.id, 0)

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


async def people_count(session: AsyncSession):
    people = await session.scalars(
        select(Person).filter(
            Person.needs_count_update == True,  # noqa: E712
        )
    )

    people_anime_counts = await session.execute(
        select(
            AnimeStaff.person_id,
            func.count()
            .filter(Anime.deleted == False)  # noqa: E712
            .label("anime_count"),
        )
        .join(Anime)
        .join(Person, Person.id == AnimeStaff.person_id)
        .filter(Person.needs_count_update == True)  # noqa: E712
        .group_by(AnimeStaff.person_id)
    )

    people_manga_counts = await session.execute(
        select(
            MangaAuthor.person_id,
            func.count()
            .filter(Manga.deleted == False)  # noqa: E712
            .label("manga_count"),
        )
        .join(Manga)
        .join(Person, Person.id == MangaAuthor.person_id)
        .filter(Person.needs_count_update == True)  # noqa: E712
        .group_by(MangaAuthor.person_id)
    )

    people_novel_counts = await session.execute(
        select(
            NovelAuthor.person_id,
            func.count()
            .filter(Novel.deleted == False)  # noqa: E712
            .label("novel_count"),
        )
        .join(Novel)
        .join(Person, Person.id == NovelAuthor.person_id)
        .filter(Person.needs_count_update == True)  # noqa: E712
        .group_by(NovelAuthor.person_id)
    )

    people_voices_counts = await session.execute(
        select(
            AnimeVoice.person_id,
            func.count()
            .filter(Anime.deleted == False)  # noqa: E712
            .label("voices_count"),
        )
        .join(Anime)
        .join(Person, Person.id == AnimeVoice.person_id)
        .filter(Person.needs_count_update == True)  # noqa: E712
        .group_by(AnimeVoice.person_id)
    )

    people_anime_count_dict = {
        person_id: count for person_id, count in people_anime_counts
    }

    people_manga_count_dict = {
        person_id: count for person_id, count in people_manga_counts
    }

    people_novel_count_dict = {
        person_id: count for person_id, count in people_novel_counts
    }

    people_voices_count_dict = {
        character_id: count for character_id, count in people_voices_counts
    }

    for person in people:
        person.anime_count = people_anime_count_dict.get(person.id, 0)

        person.manga_count = people_manga_count_dict.get(person.id, 0)

        person.novel_count = people_novel_count_dict.get(person.id, 0)

        person.voices_count = people_voices_count_dict.get(person.id, 0)

        person.needs_count_update = False

        print(
            f"Updated counts for person {person.name_en} ("
            f"{person.anime_count} / {person.manga_count} / "
            f"{person.novel_count} / {person.voices_count})"
        )

    await session.commit()


async def update_counts():
    async with sessionmanager.session() as session:
        await character_count(session)
        await people_count(session)
