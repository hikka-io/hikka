from app.models import Anime
from tortoise import Tortoise
from app import utils
from . import requests
import asyncio
import config


async def make_request(semaphore, page):
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
        slug = utils.slugify(anime_data["title"], anime_data["reference"])

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
            anime = Anime(
                **{
                    "start_date": utils.from_timestamp(
                        anime_data["start_date"]
                    ),
                    "end_date": utils.from_timestamp(anime_data["end_date"]),
                    "media_type": anime_data["media_type"],
                    "content_id": anime_data["reference"],
                    "scored_by": anime_data["scored_by"],
                    "episodes": anime_data["episodes"],
                    "title_en": anime_data["title_en"],
                    "title_ja": anime_data["title"],
                    "score": anime_data["score"],
                    "needs_update": True,
                    "updated": updated,
                    "slug": slug,
                }
            )

            create_anime.append(anime)

            print(f"Added anime: {anime.title_en}")

    await Anime.bulk_create(create_anime)

    if len(update_anime) > 0:
        await Anime.bulk_update(update_anime, fields=["needs_update"])


async def aggregator_anime():
    await Tortoise.init(config=config.tortoise)
    await Tortoise.generate_schemas()

    data = await requests.get_anime(1)
    pages = data["pagination"]["pages"]

    semaphore = asyncio.Semaphore(20)
    tasks = [make_request(semaphore, page) for page in range(1, pages + 1)]

    result = await asyncio.gather(*tasks)

    data = [item for sublist in result for item in sublist]

    await save_anime_list(data)
