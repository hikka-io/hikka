from sqlalchemy.orm import selectinload
from sqlalchemy import select
from datetime import datetime
from app import utils


from app.models import (
    AnimeRecommendation,
    AnimeStaffRole,
    AnimeCharacter,
    AnimeEpisode,
    CompanyAnime,
    AnimeGenre,
    AnimeStaff,
    AnimeVoice,
    Character,
    Company,
    Person,
    Anime,
    Image,
)


def update_if_not_ignored(model, data, field):
    if not data[field]:
        return

    if field in model.ignored_fields:
        return

    # Basically model.field = data[field] except the field is dynamic
    setattr(model, field, data[field])


def process_translations(data):
    translations = []

    for entry in data["services"]["anitube"]:
        translations.append(
            {
                "synopsis": entry["description"],
                "title": entry["title"],
                "source": entry["url"],
            }
        )

    for entry in data["services"]["toloka"]:
        translations.append(
            {
                "synopsis": entry["description"],
                "title": entry["title"],
                "source": entry["url"],
            }
        )

    return translations


async def process_genres(session, anime, data):
    genres = await session.scalars(
        select(AnimeGenre).where(AnimeGenre.content_id.in_(data["genre_ids"]))
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
        select(Company).where(Company.content_id.in_(content_ids))
    )

    companies_cache = {entry.content_id: entry for entry in cache}

    companies_anime = []

    for entry in data["companies"]:
        if not (company := companies_cache.get(entry["company"]["content_id"])):
            continue

        # ToDo: cache here
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

    cache = await session.scalars(
        select(Character).where(Character.content_id.in_(character_content_ids))
    )

    characters_cache = {entry.content_id: entry for entry in cache}

    cache = await session.scalars(
        select(Person).where(Person.content_id.in_(people_content_ids))
    )

    people_cache = {entry.content_id: entry for entry in cache}

    cache = await session.scalars(
        select(AnimeVoice).where(AnimeVoice.anime == anime)
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

        if not await session.scalar(
            select(AnimeCharacter).filter(
                AnimeCharacter.anime == anime,
                AnimeCharacter.character == character,
            )
        ):
            character_role = AnimeCharacter(
                **{
                    "character": character,
                    "main": entry["main"],
                    "anime": anime,
                }
            )

            characters_and_voices.append(character_role)

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

    return characters_and_voices


async def process_recommendations(session, anime, data):
    recommendations = []

    content_ids = [
        entry["recommended"]["content_id"] for entry in data["recommendations"]
    ]

    cache = await session.scalars(
        select(Anime).where(Anime.content_id.in_(content_ids))
    )

    recommended_cache = {entry.content_id: entry for entry in cache}

    cache = await session.scalars(
        select(AnimeRecommendation).where(AnimeRecommendation.anime == anime)
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
        select(AnimeEpisode).where(
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
                    "title_native": episode_data["title_native"],
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
            episode.title_native = episode_data["title_native"]
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
        select(Person).where(Person.content_id.in_(people_content_ids))
    )

    people_cache = {entry.content_id: entry for entry in cache}

    cache = await session.scalars(
        select(AnimeStaffRole).where(AnimeStaffRole.slug.in_(role_slugs))
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


async def process_poster(session, anime, data):
    if not (path := data.get("poster")):
        return

    if "poster" in anime.ignored_fields:
        return

    if not (poster_id := anime.poster_id):
        return

    if not (
        image := await session.scalar(
            select(Image).where(Image.id == poster_id)
        )
    ):
        return

    if image.path == path:
        return

    image = Image(
        **{
            "path": data["poster"],
            "created": datetime.utcnow(),
            "uploaded": True,
            "ignore": False,
        }
    )

    session.add(image)
    anime.poster_relation = image


async def update_anime_info(session, anime, data):
    anime.year = anime.start_date.year if anime.start_date else None
    anime.season = utils.get_season(anime.start_date)

    anime.start_date = utils.from_timestamp(data["start_date"])
    anime.end_date = utils.from_timestamp(data["end_date"])
    anime.updated = utils.from_timestamp(data["updated"])
    anime.episodes_released = data["episodes_released"]
    anime.episodes_total = data["episodes_total"]
    anime.media_type = data["media_type"]
    anime.scored_by = data["scored_by"]
    anime.duration = data["duration"]
    anime.source = data["source"]
    anime.rating = data["rating"]
    anime.status = data["status"]
    anime.score = data["score"]
    anime.nsfw = data["nsfw"]

    for field in [
        "synopsis_ua",
        "synopsis_en",
        "title_en",
        "title_ja",
        "title_ua",
        "synonyms",
        "external",
        "videos",
        "ost",
    ]:
        update_if_not_ignored(anime, data, field)

    anime.stats = data["stats"]

    await process_poster(session, anime, data)

    anime.needs_update = False

    genres_add = await process_genres(session, anime, data)

    companies_anime = await process_companies_anime(session, anime, data)

    characters_and_voices = await process_characters_and_voices(
        session, anime, data
    )

    recommendations = await process_recommendations(session, anime, data)

    episodes = await process_episodes(session, anime, data)

    update_staff = await process_staff(session, anime, data)

    session.add_all(companies_anime)
    session.add_all(characters_and_voices)
    session.add_all(update_staff)
    session.add_all(episodes)
    session.add_all(recommendations)

    for genre in genres_add:
        anime.genres.append(genre)

    session.add(anime)

    # print(f"companies_anime: {len(companies_anime)}")
    # print(f"characters_and_voices: {len(characters_and_voices)}")
    # print(f"update_staff: {len(update_staff)}")
    # print(f"episodes: {len(episodes)}")
    # print(f"recommendations: {len(recommendations)}")
    # print(f"genres_add: {len(genres_add)}")

    await session.commit()

    print(f"Synced anime {anime.title_ja}")
