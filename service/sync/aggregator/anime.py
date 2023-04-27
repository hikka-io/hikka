from service.models import AnimeGenre
from service.models import AnimeOST
from service.models import Company
from service.models import Anime
from tortoise import Tortoise
from service import utils
from . import requests
import asyncio
import config

from pprint import pprint

async def make_request_list(semaphore, page):
    async with semaphore:
        data = await requests.get_anime(page)
        return data["list"]

async def save_anime_list(data):
    references = [entry["reference"] for entry in data]

    cache = await Anime.filter(content_id__in=references)

    anime_cache = {entry.content_id: entry for entry in cache}

    create_anime = []
    update_anime = []

    for anime_data in data:
        updated = utils.from_timestamp(anime_data["updated"])
        slug = utils.slugify(
            anime_data["title"], anime_data["reference"]
        )

        if anime_data["reference"] in anime_cache:
            anime = anime_cache[anime_data["reference"]]

            if updated == anime.updated:
                continue

            if anime.needs_update:
                continue

            anime.needs_update = True
            update_anime.append(anime)

            print(f"Anime needs update: {anime.title_en}")

        else:
            anime = Anime(**{
                "start_date": utils.from_timestamp(anime_data["start_date"]),
                "end_date": utils.from_timestamp(anime_data["end_date"]),
                "media_type": anime_data["media_type"],
                "content_id": anime_data["reference"],
                "scored_by": anime_data["scored_by"],
                "episodes": anime_data["episodes"],
                "title_en": anime_data["title"],
                "score": anime_data["score"],
                "needs_update": True,
                "updated": updated,
                "slug": slug
            })

            create_anime.append(anime)

            print(f"Added anime: {anime.title_en}")

    await Anime.bulk_create(create_anime)

    if len(update_anime) > 0:
        await Anime.bulk_update(update_anime, fields=[
            "needs_update"
        ])

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
        anime.title_en = data["title"]
        anime.score = data["score"]

        anime.needs_update = False

        producers_add = []
        studios_add = []
        genres_add = []
        ost_create = []

        for genre_content_id in data["genres"]:
            if not (genre := await AnimeGenre.filter(
                content_id=genre_content_id
            ).first()):
                continue

            if genre in anime.genres:
                continue

            genres_add.append(genre)

        for studio_content_id in data["studios"]:
            if not (company := await Company.filter(
                content_id=studio_content_id
            ).first()):
                continue

            if company in anime.studios:
                continue

            studios_add.append(company)

        for producer_content_id in data["producers"]:
            if not (company := await Company.filter(
                content_id=producer_content_id
            ).first()):
                continue

            if company in anime.producers:
                continue

            producers_add.append(company)

        for song in data["ost"]:
            if await AnimeOST.filter(
                index=song["index"], anime=anime, ost_type=song["ost_type"]
            ).first():
                continue

            ost = AnimeOST(**{
                "ost_type": song["ost_type"],
                "spotify": song["spotify"],
                "author": song["author"],
                "title": song["title"],
                "index": song["index"],
                "anime": anime
            })

            ost_create.append(ost)

        if len(genres_add) > 0:
            await anime.genres.add(*genres_add)

        if len(studios_add) > 0:
            await anime.studios.add(*studios_add)

        if len(producers_add) > 0:
            await anime.producers.add(*producers_add)

        if len(ost_create) > 0:
            await AnimeOST.bulk_create(ost_create)

        await anime.save()

        print(f"Synced anime {anime.title_en}")

async def aggregator_anime():
    await Tortoise.init(config=config.tortoise)
    await Tortoise.generate_schemas()

    data = await requests.get_anime(1)
    pages = data["pagination"]["pages"]

    semaphore = asyncio.Semaphore(20)
    tasks = [make_request_list(
        semaphore, page
    ) for page in range(1, pages + 1)]

    result = await asyncio.gather(*tasks)

    data = [item for sublist in result for item in sublist]

    await save_anime_list(data)

async def aggregator_anime_info():
    await Tortoise.init(config=config.tortoise)
    await Tortoise.generate_schemas()

    anime_list = await Anime.filter(
        needs_update=True
    ).order_by("-score", "scored_by")

    semaphore = asyncio.Semaphore(20)

    tasks = [update_anime_info(semaphore, anime) for anime in anime_list]

    await asyncio.gather(*tasks)

    # data = await requests.get_anime(1)
    # pages = data["pagination"]["pages"]

    # 
    # tasks = [make_request_list(
    #     semaphore, page
    # ) for page in range(1, pages + 1)]

    # result = await asyncio.gather(*tasks)

    # data = [item for sublist in result for item in sublist]

    # await save_anime_list(data)
