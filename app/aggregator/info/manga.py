from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.utils import utcnow
from app import constants
from app import utils

from app.models import (
    MangaCharacter,
    MangaAuthor,
    AuthorRole,
    Character,
    Magazine,
    Person,
    Image,
    Genre,
    Edit,
)


async def process_genres(session, manga, data):
    genres = await session.scalars(
        select(Genre).filter(Genre.content_id.in_(data["genre_ids"]))
    )

    genres_add = []

    for genre in genres:
        if genre in manga.genres:
            continue

        genres_add.append(genre)

    return genres_add


def process_translated_ua(data):
    honey_count = len(data["honey"]) if "honey" in data else 0
    zenko_count = len(data["zenko"]) if "zenko" in data else 0
    miu_count = len(data["miu"]) if "miu" in data else 0

    return honey_count > 0 or zenko_count > 0 or miu_count > 0


def process_external(data):
    result = [
        {
            "type": constants.EXTERNAL_GENERAL,
            "text": entry["text"],
            "url": entry["url"],
        }
        for entry in data["external"]
    ]

    for source in ["honey", "zenko", "miu"]:
        website_name = {
            "miu": "Manga.in.ua",
            "honey": "Honey Manga",
            "zenko": "Zenko",
        }.get(source)

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


async def process_image(session, manga, data):
    if not data.get("poster"):
        return

    if "image" in manga.ignored_fields:
        return

    if not (
        image := await session.scalar(
            select(Image).filter(Image.path == data["poster"])
        )
    ):
        image = Image(
            **{
                "path": data["poster"],
                "created": utcnow(),
                "uploaded": True,
                "ignore": False,
            }
        )

    session.add(image)
    manga.image_relation = image


async def process_magazines(session, manga, data):
    magazines = await session.scalars(
        select(Magazine).filter(
            Magazine.mal_id.in_(
                [entry["mal_id"] for entry in data["magazines"]]
            )
        )
    )

    magazines_add = []

    for magazine in magazines:
        if magazine in manga.magazines:
            continue

        magazines_add.append(magazine)

    return magazines_add


async def process_authors(session, manga, data):
    update_authors = []

    people_content_ids = [
        entry["person"]["content_id"] for entry in data["authors"]
    ]

    role_slugs = list(
        set(
            [
                utils.slugify(role)
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
        select(MangaAuthor)
        .filter(MangaAuthor.manga == manga)
        .options(selectinload(MangaAuthor.roles))
    )

    authors_cache = {
        f"{entry.person_id}-{entry.manga_id}": entry for entry in cache
    }

    for entry in data["authors"]:
        person_content_id = entry["person"]["content_id"]

        if not (person := people_cache.get(person_content_id)):
            continue

        if not (author := authors_cache.get(f"{person.id}-{manga.id}")):
            author = MangaAuthor(
                **{
                    "person": person,
                    "manga": manga,
                }
            )

        for role_name in entry["roles"]:
            role_slug = utils.slugify(role_name)

            if not (role := role_cache.get(role_slug)):
                continue

            if role not in author.roles:
                author.roles.append(role)

        if session.is_modified(author):
            update_authors.append(author)

    return update_authors


async def process_characters(session, manga, data):
    characters = []

    character_content_ids = list(
        set([entry["character"]["content_id"] for entry in data["characters"]])
    )

    cache = await session.scalars(
        select(Character).filter(
            Character.content_id.in_(character_content_ids)
        )
    )

    characters_cache = {entry.content_id: entry for entry in cache}

    for entry in data["characters"]:
        if not (
            character := characters_cache.get(entry["character"]["content_id"])
        ):
            continue

        if character_role := await session.scalar(
            select(MangaCharacter).filter(
                MangaCharacter.manga == manga,
                MangaCharacter.character == character,
            )
        ):
            character_role.main = entry["main"]

            if session.is_modified(character_role):
                session.add(character_role)

        else:
            character_role = MangaCharacter(
                **{
                    "character": character,
                    "main": entry["main"],
                    "manga": manga,
                }
            )

            characters.append(character_role)

    return characters


def process_synonyms(data):
    result = []

    synonyms = data.get("synonyms", []) + data.get("synonyms_alt", [])

    for synonym in list(set(synonyms)):
        result.append(synonym.strip())

    return sorted(result)


async def update_manga_info(session, manga, data):
    # NOTE: this code has a lot of moving parts, hardcoded values and generaly
    # things I don't like. Let's just hope tests do cover all edge cases
    # and we will rewrite this abomination one day.

    now = utcnow()

    before = {}
    after = {}

    for field_data, field_model in [
        ["title_ja", "title_original"],
        ["synopsis_ua", "synopsis_ua"],
        ["synopsis_en", "synopsis_en"],
        ["media_type", "media_type"],
        ["title_en", "title_en"],
        ["title_ua", "title_ua"],
        ["chapters", "chapters"],
        ["volumes", "volumes"],
        ["status", "status"],
        ["nsfw", "nsfw"],
    ]:
        if field_data not in data:
            continue

        if field_model in manga.ignored_fields:
            continue

        if data[field_data] == getattr(manga, field_model):
            continue

        # If field going to be changed first we need add it to before dict
        before[field_model] = getattr(manga, field_model)

        # Update value here
        setattr(manga, field_model, data[field_data])

        # And add it to after dict
        after[field_model] = getattr(manga, field_model)

    # Extract and convert date fields
    date_fields = ["start_date", "end_date"]
    for field in date_fields:
        new_date = utils.from_timestamp(data[field])
        manga_date = getattr(manga, field)

        if manga_date != new_date and field not in manga.ignored_fields:
            before[field] = int(manga_date.timestamp()) if manga_date else None
            after[field] = int(new_date.timestamp()) if new_date else None
            setattr(manga, field, new_date)

    # Update year
    year = manga.start_date.year if manga.start_date is not None else None

    # Get external list and translated_ua status
    translated_ua = process_translated_ua(data)
    external = process_external(data)
    synonyms = process_synonyms(data)

    for field, value in [
        ("year", year),
        ("translated_ua", translated_ua),
        ("external", external),
        ("synonyms", synonyms),
    ]:
        if getattr(manga, field) != value and field not in manga.ignored_fields:
            before[field] = getattr(manga, field)
            after[field] = value
            setattr(manga, field, value)

    manga.aggregator_updated = utils.from_timestamp(data["updated"])
    manga.scored_by = data["scored_by"]
    manga.score = data["score"]
    manga.stats = data["stats"]
    manga.needs_update = False
    manga.updated = now

    await process_image(session, manga, data)

    genres_add = await process_genres(session, manga, data)
    magazines_add = await process_magazines(session, manga, data)
    update_authors = await process_authors(session, manga, data)
    characters = await process_characters(session, manga, data)

    session.add_all(update_authors)
    session.add_all(characters)

    for genre in genres_add:
        manga.genres.append(genre)

    for magazine in magazines_add:
        manga.magazines.append(magazine)

    # Only create new edit if we need to
    if before != {} and after != {}:
        edit = Edit(
            **{
                "content_type": constants.CONTENT_MANGA,
                "status": constants.EDIT_ACCEPTED,
                "content_id": manga.reference,
                "system_edit": True,
                "before": before,
                "after": after,
                "created": now,
                "updated": now,
            }
        )

        manga.needs_search_update = True

        session.add(edit)

    session.add(manga)

    # print(f"Update metadata for manga {manga.title_original}")

    await session.commit()
