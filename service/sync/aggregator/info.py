from service.models import AnimeRecommendation
from service.models import AnimeCharacter
from service.models import AnimeEpisode
from service.models import AnimeGenre
from service.models import AnimeStaff
from service.models import AnimeVoice
from service.models import Character
from service.models import Company
from service.models import Person
from service.models import Anime
from tortoise import Tortoise
from service import utils
from . import requests
import asyncio
import config

from pprint import pprint

def process_translations(data):
    translations = []

    for entry in data["services"]["anitube"]:
        translations.append({
            "synopsis": entry["description"],
            "title": entry["title"],
            "source": entry["url"]
        })

    for entry in data["services"]["toloka"]:
        translations.append({
            "synopsis": entry["description"],
            "title": entry["title"],
            "source": entry["url"]
        })

    return translations

async def process_genres(anime, data):
    genres = await AnimeGenre.filter(content_id__in=data["genres"])
    genres_add = []

    for genre in genres:
        if genre in anime.genres:
            continue

        genres_add.append(genre)

    return genres_add

async def process_studios(anime, data):
    companies = await Company.filter(content_id__in=data["studios"])
    studios_add = []

    for company in companies:
        if company in anime.studios:
            continue

        studios_add.append(company)

    return studios_add

async def process_producers(anime, data):
    companies = await Company.filter(content_id__in=data["producers"])
    producers_add = []

    for company in companies:
        if company in anime.producers:
            continue

        producers_add.append(company)

    return producers_add

async def process_characters(anime, data):
    create_character_roles = []
    create_voices = []

    cache = await Character.filter(content_id__in=[
        entry["reference"] for entry in data["characters"]
    ])

    characters_cache = {entry.content_id: entry for entry in cache}

    for character_data in data["characters"]:
        if not (character := characters_cache.get(character_data["reference"])):
            continue

        if not await AnimeCharacter.filter(
            anime=anime, character=character
        ).first():
            character_role = AnimeCharacter(**{
                "main": character_data["main"],
                "character": character,
                "anime": anime
            })

            create_character_roles.append(character_role)

        cache = await Person.filter(content_id__in=[
            entry["reference"] for entry in character_data["voice_actors"]
        ])

        voices_cache = {entry.content_id: entry for entry in cache}

        for voice_data in character_data["voice_actors"]:
            if not (person := voices_cache.get(voice_data["reference"])):
                continue

            if await AnimeVoice.filter(
                anime=anime, character=character, person=person
            ).first():
                continue

            voice = AnimeVoice(**{
                "language": voice_data["language"],
                "character": character,
                "person": person,
                "anime": anime
            })

            create_voices.append(voice)

    return create_character_roles, create_voices

async def process_recommendations(anime, data):
    create_recommendations = []
    update_recommendations = []

    cache = await Anime.filter(content_id__in=[
        entry["reference"] for entry in data["recommendations"]
    ])

    recommendations_cache = {entry.content_id: entry for entry in cache}

    for entry in data["recommendations"]:
        if not (recommended_anime := recommendations_cache.get(
            entry["reference"]
        )):
            continue

        if not (recommendation := await AnimeRecommendation.filter(
            recommendation=recommended_anime,
            anime=anime
        ).first()):
            recommendation = AnimeRecommendation(**{
                "recommendation": recommended_anime,
                "weight": entry["weight"],
                "anime": anime
            })

            create_recommendations.append(recommendation)

        else:
            if recommendation.weight == entry["weight"]:
                continue

            recommendation.weight = entry["weight"]
            update_recommendations.append(recommendation)

    return create_recommendations, update_recommendations

async def process_episodes(anime, data):
    create_episodes = []
    update_episodes = []

    cache = await AnimeEpisode.filter(anime=anime, index__in=[
        entry["index"] for entry in data["episodes_list"]
    ])

    episodes_cache = {entry.index: entry for entry in cache}

    for episode_data in data["episodes_list"]:
        if not (episode := episodes_cache.get(episode_data["index"])):
            episode = AnimeEpisode(**{
                "aired": utils.from_timestamp(episode_data["aired"]),
                "title_ja": episode_data["title_ja"],
                "title_en": episode_data["title_en"],
                "index": episode_data["index"],
                "anime": anime
            })

            create_episodes.append(episode)

        else:
            original_state = episode.__dict__.copy()

            episode.aired = utils.from_timestamp(episode_data["aired"])
            episode.title_ja = episode_data["title_ja"]
            episode.title_en = episode_data["title_en"]

            if episode.__dict__ != original_state:
                update_episodes.append(episode)

    return create_episodes, update_episodes

async def process_staff(anime, data):
    create_staff = []

    cache = await Person.filter(content_id__in=[
        entry["person_reference"] for entry in data["staff"]
    ])

    people_cache = {entry.content_id: entry for entry in cache}

    for entry in data["staff"]:
        if not (person := people_cache.get(
            entry["person_reference"]
        )):
            continue

        if await AnimeStaff.filter(anime=anime, person=person).first():
            continue

        staff = AnimeStaff(**{
            "role": entry["role"],
            "person": person,
            "anime": anime
        })

        create_staff.append(staff)

    return create_staff

async def update_anime_info(semaphore, anime):
    async with semaphore:
        await anime.fetch_related("genres", "studios", "producers")

        data = await requests.get_anime_info(anime.content_id)

        anime.start_date = utils.from_timestamp(data["start_date"])
        anime.end_date = utils.from_timestamp(data["end_date"])
        anime.updated = utils.from_timestamp(data["updated"])
        anime.media_type = data["media_type"]
        anime.scored_by = data["scored_by"]
        anime.episodes = data["episodes"]
        anime.duration = data["duration"]
        anime.source = data["source"]
        anime.rating = data["rating"]
        anime.score = data["score"]
        anime.nsfw = data["nsfw"]

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

        anime.needs_update = False

        producers_add = await process_producers(anime, data)
        studios_add = await process_studios(anime, data)
        genres_add = await process_genres(anime, data)

        create_character_roles, create_voices = await process_characters(
            anime, data
        )

        create_recommendations, update_recommendations = await process_recommendations(
            anime, data
        )

        create_episodes, update_episodes = await process_episodes(anime, data)

        create_staff = await process_staff(anime, data)

        if len(create_character_roles) > 0:
            await AnimeCharacter.bulk_create(create_character_roles)

        if len(create_voices) > 0:
            await AnimeVoice.bulk_create(create_voices)

        if len(create_staff) > 0:
            await AnimeStaff.bulk_create(create_staff)

        if len(create_episodes) > 0:
            await AnimeEpisode.bulk_create(create_episodes)

        if len(create_recommendations) > 0:
            await AnimeRecommendation.bulk_create(create_recommendations)

        if len(genres_add) > 0:
            await anime.genres.add(*genres_add)

        if len(studios_add) > 0:
            await anime.studios.add(*studios_add)

        if len(producers_add) > 0:
            await anime.producers.add(*producers_add)

        if len(update_recommendations) > 0:
            await AnimeRecommendation.bulk_update(
                update_recommendations, fields=["weight"]
            )

        if len(update_episodes) > 0:
            await AnimeEpisode.bulk_update(update_episodes, fields=[
                "title_ja", "title_en", "aired"
            ])

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

        await anime.save()

        print(f"Synced anime {anime.title_en}")

async def aggregator_anime_info():
    await Tortoise.init(config=config.tortoise)
    await Tortoise.generate_schemas()
    
    # anime = await Anime.filter(content_id="354966ae-28ee-496f-8a55-f088f65396b4").first()
    # semaphore = asyncio.Semaphore(20)
    # await update_anime_info(semaphore, anime)

    semaphore = asyncio.Semaphore(20)

    anime_list = await Anime.filter(
        needs_update=True
    ).order_by("-score", "scored_by")

    tasks = [update_anime_info(semaphore, anime) for anime in anime_list]

    await asyncio.gather(*tasks)
