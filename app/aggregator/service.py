from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import chunkify, utcnow, slugify
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app import constants

from app.models import (
    MangaCharacter,
    NovelCharacter,
    MangaAuthor,
    NovelAuthor,
    AuthorRole,
    Character,
    Magazine,
    Person,
    Anime,
    Manga,
    Novel,
    Image,
    Genre,
)


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


async def process_genres(
    session: AsyncSession, content: Manga | Novel, data: dict
):
    genres = await session.scalars(
        select(Genre).filter(Genre.content_id.in_(data["genre_ids"]))
    )

    genres_add = []

    for genre in genres:
        if genre in content.genres:
            continue

        genres_add.append(genre)

    return genres_add


async def process_magazines(
    session: AsyncSession, content: Manga | Novel, data: dict
):
    magazines = await session.scalars(
        select(Magazine).filter(
            Magazine.mal_id.in_(
                [entry["mal_id"] for entry in data["magazines"]]
            )
        )
    )

    magazines_add = []

    for magazine in magazines:
        if magazine in content.magazines:
            continue

        magazines_add.append(magazine)

    return magazines_add


async def process_authors(
    session: AsyncSession,
    content: Manga | Novel,
    author_model: type[MangaAuthor] | type[NovelAuthor],
    data: dict,
):
    update_authors = []

    # Author rows point to content by its type (manga or novel)
    content_relation = getattr(author_model, content.data_type)

    people_content_ids = [
        entry["person"]["content_id"] for entry in data["authors"]
    ]

    role_slugs = list(
        set(
            [
                slugify(role)
                for tmp_roles in [entry["roles"] for entry in data["authors"]]
                for role in tmp_roles
            ]
        )
    )

    cache = await session.scalars(
        select(Person).filter(Person.content_id.in_(people_content_ids))
    )

    people_cache = {entry.content_id: entry for entry in cache}

    cache = await session.scalars(
        select(AuthorRole).filter(AuthorRole.slug.in_(role_slugs))
    )

    role_cache = {entry.slug: entry for entry in cache}

    cache = await session.scalars(
        select(author_model)
        .filter(content_relation == content)
        .options(selectinload(author_model.roles))
    )

    # Every row belongs to this content and person alone is enough as key
    authors_cache = {entry.person_id: entry for entry in cache}

    for entry in data["authors"]:
        person_content_id = entry["person"]["content_id"]

        if not (person := people_cache.get(person_content_id)):
            continue

        if not (author := authors_cache.get(person.id)):
            author = author_model(
                **{
                    "person": person,
                    content.data_type: content,
                }
            )

            person.needs_count_update = True

        for role_name in entry["roles"]:
            role_slug = slugify(role_name)

            if not (role := role_cache.get(role_slug)):
                continue

            if role not in author.roles:
                author.roles.append(role)

        if session.is_modified(author):
            update_authors.append(author)

    return update_authors


async def process_characters(
    session: AsyncSession,
    content: Manga | Novel,
    character_model: type[MangaCharacter] | type[NovelCharacter],
    data: dict,
):
    characters = []

    # Character rows point to content by its type (manga or novel)
    content_relation = getattr(character_model, content.data_type)

    character_content_ids = list(
        set([entry["character"]["content_id"] for entry in data["characters"]])
    )

    characters_cache = await get_characters_cache(
        session, character_content_ids
    )

    cache = await session.scalars(
        select(character_model).filter(content_relation == content)
    )

    existing_characters = {entry.character_id: entry.id for entry in cache}

    actual_character_ids = set()

    for entry in data["characters"]:
        if not (
            character := characters_cache.get(entry["character"]["content_id"])
        ):
            continue

        if character_role := await session.scalar(
            select(character_model).filter(
                content_relation == content,
                character_model.character == character,
            )
        ):
            character_role.main = entry["main"]

            if session.is_modified(character_role):
                session.add(character_role)

        else:
            character_role = character_model(
                **{
                    "character": character,
                    "main": entry["main"],
                    content.data_type: content,
                }
            )

            characters.append(character_role)

            character.needs_count_update = True

        actual_character_ids.add(character.id)

    bad_character_ids = set(existing_characters.keys()) - actual_character_ids

    for character_id in bad_character_ids:
        await session.execute(
            delete(character_model).filter(
                character_model.id == existing_characters[character_id]
            )
        )

    # Removed characters have to be recounted
    await mark_count_update(session, Character, bad_character_ids)

    return characters


def process_synonyms(data: dict):
    result = []

    synonyms = data.get("synonyms", []) + data.get("synonyms_alt", [])

    for synonym in list(set(synonyms)):
        result.append(synonym.strip())

    return sorted(result)


def process_translated_ua(data: dict, sources: list[str]):
    return any(len(data.get(source, [])) > 0 for source in sources)


def process_external(data: dict, read_sources: dict[str, str]):
    result = [
        {
            "type": constants.EXTERNAL_GENERAL,
            "text": entry["text"],
            "url": entry["url"],
        }
        for entry in data["external"]
    ]

    for source, website_name in read_sources.items():
        result.extend(
            [
                {
                    "type": constants.EXTERNAL_READ,
                    "text": website_name,
                    "url": entry["url"],
                }
                for entry in data.get(source, [])
            ]
        )

    return result
