from app.models import NovelCharacter, NovelAuthor, Edit
from app.aggregator import service
from app.utils import utcnow
from app import constants
from app import utils

# Ukrainian sources which mark novel as translated
translated_ua_sources = ["dgmanga", "honey", "baka"]

# Read links added to external in this order
read_sources = {
    "baka": "Бака",
    "zenko": "Zenko",
    "dgmanga": "DGManga",
}


async def update_novel_info(session, novel, data):
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

        if field_model in novel.ignored_fields:
            continue

        if data[field_data] == getattr(novel, field_model):
            continue

        # If field going to be changed first we need add it to before dict
        before[field_model] = getattr(novel, field_model)

        # Update value here
        setattr(novel, field_model, data[field_data])

        # And add it to after dict
        after[field_model] = getattr(novel, field_model)

    # Extract and convert date fields
    date_fields = ["start_date", "end_date"]
    for field in date_fields:
        new_date = utils.from_timestamp(data[field])
        novel_date = getattr(novel, field)

        if novel_date != new_date and field not in novel.ignored_fields:
            before[field] = int(novel_date.timestamp()) if novel_date else None
            after[field] = int(new_date.timestamp()) if new_date else None
            setattr(novel, field, new_date)

    # Update year
    year = novel.start_date.year if novel.start_date is not None else None

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
        if getattr(novel, field) != value and field not in novel.ignored_fields:
            before[field] = getattr(novel, field)
            after[field] = value
            setattr(novel, field, value)

    novel.aggregator_updated = utils.from_timestamp(data["updated"])
    novel.scored_by = data["scored_by"]
    novel.score = data["score"]
    novel.stats = data["stats"]
    novel.needs_update = False
    novel.updated = now

    await service.process_image(session, novel, data)

    genres_add = await service.process_genres(session, novel, data)
    magazines_add = await service.process_magazines(session, novel, data)
    update_authors = await service.process_authors(
        session, novel, NovelAuthor, data
    )
    characters = await service.process_characters(
        session, novel, NovelCharacter, data
    )

    session.add_all(update_authors)
    session.add_all(characters)

    for genre in genres_add:
        novel.genres.append(genre)

    for magazine in magazines_add:
        novel.magazines.append(magazine)

    # Only create new edit if we need to
    if before != {} and after != {}:
        edit = Edit(
            **{
                "content_type": constants.CONTENT_NOVEL,
                "status": constants.EDIT_ACCEPTED,
                "content_id": novel.reference,
                "system_edit": True,
                "before": before,
                "after": after,
                "created": now,
                "updated": now,
            }
        )

        novel.needs_search_update = True

        session.add(edit)

    session.add(novel)

    # print(f"Update metadata for novel {novel.title_original}")

    await session.commit()
