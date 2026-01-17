from sqlalchemy.orm import selectinload
from app.aggregator import service
from sqlalchemy import select
from app.utils import utcnow
from app import constants
from app import utils

from app.models import (
    AnimeRecommendation,
    AnimeStaffRole,
    AnimeCharacter,
    AnimeEpisode,
    CompanyAnime,
    AnimeStaff,
    AnimeVoice,
    Company,
    Person,
    Genre,
    Anime,
    Image,
    Edit,
)


async def process_genres(session, anime, data):
    genres = await session.scalars(
        select(Genre).filter(Genre.content_id.in_(data["genre_ids"]))
    )

    genres_add = []

    for genre in genres:
        if genre in anime.genres:
            continue

        genres_add.append(genre)

    return genres_add


async def process_companies_anime(session, anime, data):
    content_ids = [
        company["company"]["content_id"] for company in data["companies"]
    ]

    cache = await session.scalars(
        select(Company).filter(Company.content_id.in_(content_ids))
    )

    companies_cache = {entry.content_id: entry for entry in cache}

    companies_anime = []

    for entry in data["companies"]:
        if not (company := companies_cache.get(entry["company"]["content_id"])):
            continue

        # TODO: cache here
        if await session.scalar(
            select(CompanyAnime).filter(
                CompanyAnime.type == entry["type"],
                CompanyAnime.company == company,
                CompanyAnime.anime == anime,
            )
        ):
            continue

        company_anime = CompanyAnime(
            **{
                "type": entry["type"],
                "company": company,
                "anime": anime,
            }
        )

        companies_anime.append(company_anime)

    return companies_anime


async def process_characters_and_voices(session, anime, data):
    characters_and_voices = []

    character_content_ids = list(
        set([entry["character"]["content_id"] for entry in data["characters"]])
    )

    people_content_ids = list(
        set([entry["person"]["content_id"] for entry in data["voices"]])
    )

    characters_cache = await service.get_characters_cache(
        session, character_content_ids
    )

    cache = await session.scalars(
        select(Person).filter(Person.content_id.in_(people_content_ids))
    )

    people_cache = {entry.content_id: entry for entry in cache}

    cache = await session.scalars(
        select(AnimeVoice).filter(AnimeVoice.anime == anime)
    )

    anime_voice_cache = {
        f"{entry.character_id}-{entry.person_id}-{entry.language}": entry
        for entry in cache
    }

    # Assign people to characters to make import logic easier
    voices = {}

    for entry in data["voices"]:
        character_content_id = entry["character"]["content_id"]
        person_content_id = entry["person"]["content_id"]

        if character_content_id not in voices:
            voices[character_content_id] = []

        if person_content_id not in voices[character_content_id]:
            voices[character_content_id].append(
                {
                    "person_content_id": person_content_id,
                    "language": entry["language"],
                }
            )

    for entry in data["characters"]:
        if not (
            character := characters_cache.get(entry["character"]["content_id"])
        ):
            continue

        if character_role := await session.scalar(
            select(AnimeCharacter).filter(
                AnimeCharacter.anime == anime,
                AnimeCharacter.character == character,
            )
        ):
            character_role.main = entry["main"]

            if session.is_modified(character_role):
                session.add(character_role)

        else:
            character_role = AnimeCharacter(
                **{
                    "character": character,
                    "main": entry["main"],
                    "anime": anime,
                }
            )

            characters_and_voices.append(character_role)

            character.needs_count_update = True

        if character.content_id not in voices:
            continue

        for entry in voices[character.content_id]:
            person_content_id = entry["person_content_id"]
            language = entry["language"]

            if not (person := people_cache.get(person_content_id)):
                continue

            if anime_voice_cache.get(f"{character.id}-{person.id}-{language}"):
                continue

            voice = AnimeVoice(
                **{
                    "character": character,
                    "language": language,
                    "person": person,
                    "anime": anime,
                }
            )

            characters_and_voices.append(voice)

            character.needs_count_update = True
            person.needs_count_update = True

    return characters_and_voices


async def process_recommendations(session, anime, data):
    recommendations = []

    content_ids = [
        entry["recommended"]["content_id"] for entry in data["recommendations"]
    ]

    cache = await session.scalars(
        select(Anime).filter(Anime.content_id.in_(content_ids))
    )

    recommended_cache = {entry.content_id: entry for entry in cache}

    cache = await session.scalars(
        select(AnimeRecommendation).filter(AnimeRecommendation.anime == anime)
    )

    recommendations_cache = {
        f"{entry.recommendation_id}-{entry.anime_id}": entry for entry in cache
    }

    for entry in data["recommendations"]:
        if not (
            recommended := recommended_cache.get(
                entry["recommended"]["content_id"]
            )
        ):
            continue

        if recommendation := recommendations_cache.get(
            f"{recommended.id}-{anime.id}"
        ):
            if recommendation.weight == entry["weight"]:
                continue

            recommendation.weight = entry["weight"]
            recommendations.append(recommendation)

        else:
            recommendations.append(
                AnimeRecommendation(
                    **{
                        "recommendation": recommended,
                        "weight": entry["weight"],
                        "anime": anime,
                    }
                )
            )

    return recommendations


async def process_episodes(session, anime, data):
    episodes = []

    cache = await session.scalars(
        select(AnimeEpisode).filter(
            AnimeEpisode.anime == anime,
            AnimeEpisode.index.in_(
                [entry["index"] for entry in data["episodes_list"]]
            ),
        )
    )

    episodes_cache = {entry.index: entry for entry in cache}

    for episode_data in data["episodes_list"]:
        if not (episode := episodes_cache.get(episode_data["index"])):
            episode = AnimeEpisode(
                **{
                    "aired": utils.from_timestamp(episode_data["aired"]),
                    "title_ja": episode_data["title_ja"],
                    "title_en": episode_data["title_en"],
                    "title_ua": episode_data["title_ua"],
                    "index": episode_data["index"],
                    "anime": anime,
                }
            )

            episodes.append(episode)

        else:
            episode.aired = utils.from_timestamp(episode_data["aired"])
            episode.title_ja = episode_data["title_ja"]
            episode.title_en = episode_data["title_en"]
            episode.title_ua = episode_data["title_ua"]

            if session.is_modified(episode):
                episodes.append(episode)

    return episodes


async def process_staff(session, anime, data):
    update_staff = []

    people_content_ids = [
        entry["person"]["content_id"] for entry in data["staff"]
    ]

    role_slugs = list(
        set(
            [
                utils.slugify(role)
                for tmp_roles in [entry["roles"] for entry in data["staff"]]
                for role in tmp_roles
            ]
        )
    )

    cache = await session.scalars(
        select(Person).filter(Person.content_id.in_(people_content_ids))
    )

    people_cache = {entry.content_id: entry for entry in cache}

    cache = await session.scalars(
        select(AnimeStaffRole).filter(AnimeStaffRole.slug.in_(role_slugs))
    )

    role_cache = {entry.slug: entry for entry in cache}

    cache = await session.scalars(
        select(AnimeStaff)
        .filter(AnimeStaff.anime == anime)
        .options(selectinload(AnimeStaff.roles))
    )

    staff_cache = {
        f"{entry.person_id}-{entry.anime_id}": entry for entry in cache
    }

    for entry in data["staff"]:
        person_content_id = entry["person"]["content_id"]

        if not (person := people_cache.get(person_content_id)):
            continue

        if not (staff := staff_cache.get(f"{person.id}-{anime.id}")):
            staff = AnimeStaff(
                **{
                    "person": person,
                    "anime": anime,
                }
            )

        for role_name in entry["roles"]:
            role_slug = utils.slugify(role_name)

            if not (role := role_cache.get(role_slug)):
                continue

            if role not in staff.roles:
                staff.roles.append(role)

        if session.is_modified(staff):
            update_staff.append(staff)

    return update_staff


async def process_image(session, anime, data):
    if not data.get("poster"):
        return

    if "poster" in anime.ignored_fields:
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
                "system": True,
            }
        )

    session.add(image)
    anime.image_relation = image


def process_external(data):
    result = [
        {
            "type": constants.EXTERNAL_GENERAL,
            "text": entry["text"],
            "url": entry["url"],
        }
        for entry in data["external"]
    ]

    for source in ["anitube", "toloka", "mikai"]:
        website_name = {
            "anitube": "Anitube",
            "toloka": "Toloka",
            "mikai": "Mikai",
        }.get(source)

        result.extend(
            [
                {
                    "type": constants.EXTERNAL_WATCH,
                    "text": website_name,
                    "url": entry["url"],
                }
                for entry in data.get(source, [])
            ]
        )

    return result


def process_translated_ua(data):
    # Ideally we should make some loop here or something like that
    # Not this
    anitube_len = len(data["anitube"]) if "anitube" in data else 0
    toloka_len = len(data["toloka"]) if "toloka" in data else 0
    mikai_len = len(data["mikai"]) if "mikai" in data else 0
    return anitube_len > 0 or toloka_len > 0 or mikai_len > 0


async def update_anime_info(session, anime, data):
    # NOTE: this code has a lot of moving parts, hardcoded values and generaly
    # things I don't like. Let's just hope tests do cover all edge cases
    # and we will rewrite this abomination one day.

    now = utcnow()

    before = {}
    after = {}

    for field in [
        "episodes_released",
        "episodes_total",
        "synopsis_ua",
        "synopsis_en",
        "media_type",
        "schedule",
        "duration",
        "title_en",
        "title_ja",
        "title_ua",
        "synonyms",
        "source",
        "rating",
        "status",
        "videos",
        "nsfw",
        "ost",
    ]:
        if field not in data:
            continue

        if field in anime.ignored_fields:
            continue

        if data[field] == getattr(anime, field):
            continue

        # Special checks to prevent overwriting
        # changes made by our anime schedule task
        if field == "episodes_released":
            if (
                data[field] is not None
                and getattr(anime, field)
                and getattr(anime, field) > data[field]
            ):
                continue

        if field == "status":
            if getattr(anime, field) == constants.RELEASE_STATUS_FINISHED:
                continue

        # If field going to be changed first we need add it to before dict
        before[field] = getattr(anime, field)

        # Update value here
        setattr(anime, field, data[field])

        # And add it to after dict
        after[field] = getattr(anime, field)

    # Special case (awful hack) for situations when
    # schedule logic don't update episodes_released field properly
    # while holding it hostage in ignored fields
    if (
        anime.status == constants.RELEASE_STATUS_FINISHED
        and anime.episodes_total is not None
        and (
            anime.episodes_released is None
            or anime.episodes_released < anime.episodes_total
        )
    ):
        anime.episodes_released = anime.episodes_total

    # Yet another special case (abhorent hack) for handling schedule bugs
    if (
        anime.status != constants.RELEASE_STATUS_FINISHED
        and data["status"] == constants.RELEASE_STATUS_FINISHED
    ):
        anime.status = constants.RELEASE_STATUS_FINISHED

        if anime.episodes_total is not None:
            anime.episodes_released = anime.episodes_total

    # At this point I just hate schedule subsystem with my whole heart
    if anime.episodes_total is not None:
        anime.schedule = [
            entry
            for entry in anime.schedule
            if entry["episode"] <= anime.episodes_total
        ]

    # Extract and convert date fields
    date_fields = ["start_date", "end_date"]
    for field in date_fields:
        new_date = utils.from_timestamp(data[field])
        anime_date = getattr(anime, field)

        if anime_date != new_date and field not in anime.ignored_fields:
            before[field] = int(anime_date.timestamp()) if anime_date else None
            after[field] = int(new_date.timestamp()) if new_date else None
            setattr(anime, field, new_date)

    # Update year and season fields
    if anime.start_date:
        # Special case for titles starting in less than 7 days before new season
        start_date = anime.start_date
        if utils.days_until_next_month(start_date) < 7:
            start_date = utils.get_next_month(start_date)

        year = start_date.year
        season = utils.get_season(start_date)
        airing_seasons = [f"{season}_{year}"]

        if anime.end_date is not None:
            airing_seasons = utils.get_airing_seasons(
                anime.start_date, anime.end_date
            )

    else:
        year = None
        season = None
        airing_seasons = []

    # Get external list and translated_ua status
    translated_ua = process_translated_ua(data)
    external = process_external(data)

    for field, value in [
        ("year", year),
        ("season", season),
        ("translated_ua", translated_ua),
        ("external", external),
    ]:
        if getattr(anime, field) != value and field not in anime.ignored_fields:
            before[field] = getattr(anime, field)
            after[field] = value
            setattr(anime, field, value)

    anime.aggregator_updated = utils.from_timestamp(data["updated"])
    anime.airing_seasons = airing_seasons
    anime.scored_by = data["scored_by"]
    anime.score = data["score"]
    anime.stats = data["stats"]
    anime.needs_update = False
    anime.updated = now

    await process_image(session, anime, data)

    genres_add = await process_genres(session, anime, data)
    companies_anime = await process_companies_anime(session, anime, data)
    recommendations = await process_recommendations(session, anime, data)
    episodes = await process_episodes(session, anime, data)
    update_staff = await process_staff(session, anime, data)
    characters_and_voices = await process_characters_and_voices(
        session, anime, data
    )

    session.add_all(characters_and_voices)
    session.add_all(recommendations)
    session.add_all(companies_anime)
    session.add_all(update_staff)
    session.add_all(episodes)

    for genre in genres_add:
        anime.genres.append(genre)

    # Only create new edit if we need to
    if before != {} and after != {}:
        edit = Edit(
            **{
                "content_type": constants.CONTENT_ANIME,
                "status": constants.EDIT_ACCEPTED,
                "content_id": anime.reference,
                "system_edit": True,
                "before": before,
                "after": after,
                "created": now,
                "updated": now,
            }
        )

        anime.needs_search_update = True

        session.add(edit)

    session.add(anime)

    await session.commit()
