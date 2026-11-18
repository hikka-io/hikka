from app.models import MangaCharacter, MangaAuthor, Edit
from app.aggregator import service
from app.utils import utcnow
from app import constants
from app import utils

# Ukrainian sources which mark manga as translated
translated_ua_sources = ["dgmanga", "honey", "zenko", "miu"]

# Read links added to external in this order
read_sources = {
    "zenko": "Zenko",
    "miu": "Manga.in.ua",
    "dgmanga": "DGManga",
}


async def update_manga_info(session, manga, data):
    # NOTE: this code has a lot of moving parts, hardcoded values and generaly
    # things I don't like. Let's just hope tests do cover all edge cases
    # and we will rewrite this abomination one day.

    now = utcnow()

    before = {}
    after = {}

    for field_data, field_model in [
        ["title_native", "title_native"],
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
    translated_ua = service.process_translated_ua(data, translated_ua_sources)
    external = service.process_external(data, read_sources)
    synonyms = service.process_synonyms(data)

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

    await service.process_image(session, manga, data)

    genres_add = await service.process_genres(session, manga, data)
    magazines_add = await service.process_magazines(session, manga, data)
    update_authors = await service.process_authors(
        session, manga, MangaAuthor, data
    )
    characters = await service.process_characters(
        session, manga, MangaCharacter, data
    )

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
