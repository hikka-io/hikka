from app.models import AnimeRecommendation
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from app.models import AnimeCharacter
from sqlalchemy import select, desc
from app.models import AnimeEpisode
from app.models import AnimeGenre
from app.models import AnimeStaff
from app.models import AnimeVoice
from app.models import Character
from app.models import Company
from datetime import datetime
from app.models import Person
from app.models import Anime
from app.models import Image
from . import requests
from app import utils
import asyncio
import config


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
        select(AnimeGenre).where(AnimeGenre.content_id.in_(data["genres"]))
    )

    genres_add = []

    for genre in genres:
        if genre in anime.genres:
            continue

        genres_add.append(genre)

    return genres_add


async def process_studios(session, anime, data):
    companies = await session.scalars(
        select(Company).where(Company.content_id.in_(data["studios"]))
    )

    studios_add = []

    for company in companies:
        if company in anime.studios:
            continue

        studios_add.append(company)

    return studios_add


async def process_producers(session, anime, data):
    companies = await session.scalars(
        select(Company).where(Company.content_id.in_(data["producers"]))
    )

    producers_add = []

    for company in companies:
        if company in anime.producers:
            continue

        producers_add.append(company)

    return producers_add


async def process_characters(session, anime, data):
    create_character_roles = []
    create_voices = []

    cache = await session.scalars(
        select(Character).where(
            Character.content_id.in_(
                [entry["reference"] for entry in data["characters"]]
            )
        )
    )

    characters_cache = {entry.content_id: entry for entry in cache}

    for character_data in data["characters"]:
        if not (character := characters_cache.get(character_data["reference"])):
            continue

        if not await session.scalar(
            select(AnimeCharacter).filter_by(anime=anime, character=character)
        ):
            character_role = AnimeCharacter(
                **{
                    "main": character_data["main"],
                    "character": character,
                    "anime": anime,
                }
            )

            create_character_roles.append(character_role)

        cache = await session.scalars(
            select(Person).where(
                Person.content_id.in_(
                    [
                        entry["reference"]
                        for entry in character_data["voice_actors"]
                    ]
                )
            )
        )

        voices_cache = {entry.content_id: entry for entry in cache}

        for voice_data in character_data["voice_actors"]:
            if not (person := voices_cache.get(voice_data["reference"])):
                continue

            if await session.scalar(
                select(AnimeVoice).filter_by(
                    anime=anime, character=character, person=person
                )
            ):
                continue

            voice = AnimeVoice(
                **{
                    "language": voice_data["language"],
                    "character": character,
                    "person": person,
                    "anime": anime,
                }
            )

            create_voices.append(voice)

    return create_character_roles, create_voices


async def process_recommendations(session, anime, data):
    create_recommendations = []
    update_recommendations = []

    cache = await session.scalars(
        select(Anime).where(
            Anime.content_id.in_(
                [entry["reference"] for entry in data["recommendations"]]
            )
        )
    )

    recommendations_cache = {entry.content_id: entry for entry in cache}

    for entry in data["recommendations"]:
        if not (
            recommended_anime := recommendations_cache.get(entry["reference"])
        ):
            continue

        if not (
            recommendation := await session.scalar(
                select(AnimeRecommendation).filter_by(
                    recommendation=recommended_anime, anime=anime
                )
            )
        ):
            recommendation = AnimeRecommendation(
                **{
                    "recommendation": recommended_anime,
                    "weight": entry["weight"],
                    "anime": anime,
                }
            )

            create_recommendations.append(recommendation)

        else:
            if recommendation.weight == entry["weight"]:
                continue

            recommendation.weight = entry["weight"]
            update_recommendations.append(recommendation)

    return create_recommendations, update_recommendations


async def process_episodes(session, anime, data):
    create_episodes = []
    update_episodes = []

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
                    "title_ja": episode_data["title_ja"],
                    "title_en": episode_data["title_en"],
                    "index": episode_data["index"],
                    "anime": anime,
                }
            )

            create_episodes.append(episode)

        else:
            original_state = episode.__dict__.copy()

            episode.aired = utils.from_timestamp(episode_data["aired"])
            episode.title_ja = episode_data["title_ja"]
            episode.title_en = episode_data["title_en"]

            if episode.__dict__ != original_state:
                update_episodes.append(episode)

    return create_episodes, update_episodes


async def process_staff(session, anime, data):
    create_staff = []

    cache = await session.scalars(
        select(Person).where(
            Person.content_id.in_(
                [entry["person_reference"] for entry in data["staff"]]
            )
        )
    )

    people_cache = {entry.content_id: entry for entry in cache}

    for entry in data["staff"]:
        if not (person := people_cache.get(entry["person_reference"])):
            continue

        if await session.scalar(
            select(AnimeStaff).filter_by(anime=anime, person=person)
        ):
            continue

        staff = AnimeStaff(
            **{"role": entry["role"], "person": person, "anime": anime}
        )

        create_staff.append(staff)

    return create_staff


async def update_anime_info(semaphore, content_id):
    async with semaphore:
        sessionmanager.init(config.database)

        async with sessionmanager.session() as session:
            anime = await session.scalar(
                select(Anime)
                .filter_by(content_id=content_id)
                .options(
                    selectinload(Anime.studios),
                    selectinload(Anime.producers),
                    selectinload(Anime.genres),
                )
            )

            data = await requests.get_anime_info(anime.content_id)

            total_episodes = len(data["episodes_list"])

            anime.year = anime.start_date.year if anime.start_date else None
            anime.season = utils.get_season(anime.start_date)

            anime.start_date = utils.from_timestamp(data["start_date"])
            anime.end_date = utils.from_timestamp(data["end_date"])
            anime.updated = utils.from_timestamp(data["updated"])
            anime.media_type = data["media_type"]
            anime.scored_by = data["scored_by"]
            anime.episodes = data["episodes"]
            anime.duration = data["duration"]
            anime.source = data["source"]
            anime.rating = data["rating"]
            anime.status = data["status"]
            anime.score = data["score"]
            anime.nsfw = data["nsfw"]

            anime.total_episodes = (
                total_episodes if total_episodes > 0 else None
            )

            anime.synopsis_en = data["synopsis"]
            anime.title_en = data["title_en"]
            anime.title_ja = data["title"]

            # ToDo: add extra checks here
            anime.translations = process_translations(data)
            anime.synonyms = data["synonyms"]
            anime.external = data["external"]
            anime.videos = data["videos"]
            anime.stats = data["stats"]
            anime.ost = data["ost"]

            if data["poster"]:
                if not (
                    image := await session.scalar(
                        select(Image).filter_by(path=data["poster"])
                    )
                ):
                    image = Image(
                        **{
                            "created": datetime.utcnow(),
                            "path": data["poster"],
                        }
                    )

                anime.poster = image

            anime.needs_update = False

            producers_add = await process_producers(session, anime, data)
            studios_add = await process_studios(session, anime, data)
            genres_add = await process_genres(session, anime, data)

            create_character_roles, create_voices = await process_characters(
                session, anime, data
            )

            (
                create_recommendations,
                update_recommendations,
            ) = await process_recommendations(session, anime, data)

            create_episodes, update_episodes = await process_episodes(
                session, anime, data
            )

            create_staff = await process_staff(session, anime, data)

            if len(create_character_roles) > 0:
                session.add_all(create_character_roles)

            if len(create_voices) > 0:
                session.add_all(create_voices)

            if len(create_staff) > 0:
                session.add_all(create_staff)

            if len(create_episodes) > 0:
                session.add_all(create_episodes)

            if len(create_recommendations) > 0:
                session.add_all(create_recommendations)

            for genre in genres_add:
                anime.genres.append(genre)

            for company in studios_add:
                anime.studios.append(company)

            for company in producers_add:
                anime.producers.append(company)

            if len(update_recommendations) > 0:
                session.add_all(update_recommendations)

            if len(update_episodes) > 0:
                session.add_all(update_episodes)

            session.add(anime)

            # print(f"create_character_roles: {len(create_character_roles)}")
            # print(f"create_voices: {len(create_voices)}")
            # print(f"create_staff: {len(create_staff)}")
            # print(f"create_episodes: {len(create_episodes)}")
            # print(f"create_recommendations: {len(create_recommendations)}")
            # print(f"genres_add: {len(genres_add)}")
            # print(f"studios_add: {len(studios_add)}")
            # print(f"producers_add: {len(producers_add)}")
            # print(f"update_recommendations: {len(update_recommendations)}")
            # print(f"update_episodes: {len(update_episodes)}")

            await session.commit()

            print(f"Synced anime {anime.title_ja}")


async def aggregator_anime_info():
    sessionmanager.init(config.database)
    anime_list = []

    async with sessionmanager.session() as session:
        anime_list = await session.scalars(
            select(Anime.content_id)
            .filter_by(needs_update=True)
            .order_by(desc("score"), desc("scored_by"))
        )

    semaphore = asyncio.Semaphore(10)

    tasks = [
        update_anime_info(semaphore, content_id) for content_id in anime_list
    ]

    await asyncio.gather(*tasks)
