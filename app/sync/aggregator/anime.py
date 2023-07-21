from app.database import sessionmanager
from app.models import Anime, Image
from sqlalchemy import select
from datetime import datetime
from . import requests
from app import utils
import asyncio
import config


async def make_request(semaphore, page):
    async with semaphore:
        data = await requests.get_anime(page)
        return data["list"]


async def save_anime_list(data):
    sessionmanager.init(config.database)

    async with sessionmanager.session() as session:
        content_ids = [entry["content_id"] for entry in data]
        posters = [entry["poster"] for entry in data]

        cache = await session.scalars(
            select(Anime).where(Anime.content_id.in_(content_ids))
        )

        anime_cache = {entry.content_id: entry for entry in cache}

        cache = await session.scalars(
            select(Image).where(Image.path.in_(posters))
        )

        poster_cache = {entry.path: entry for entry in cache}

        add_anime = []

        for anime_data in data:
            updated = utils.from_timestamp(anime_data["updated"])
            slug = utils.slugify(
                anime_data["title_ja"], anime_data["content_id"]
            )

            if anime_data["content_id"] in anime_cache:
                anime = anime_cache[anime_data["content_id"]]

                if updated == anime.updated:
                    continue

                if anime.needs_update:
                    continue

                anime.needs_update = True

                add_anime.append(anime)

                print(f"Anime needs update: {anime.title_en}")

            else:
                if not (image := poster_cache.get(anime_data["poster"])):
                    if anime_data["poster"]:
                        image = Image(
                            **{
                                "path": anime_data["poster"],
                                "created": datetime.utcnow(),
                                "uploaded": True,
                                "ignore": False,
                            }
                        )

                        poster_cache[anime_data["poster"]] = image

                start_date = utils.from_timestamp(anime_data["start_date"])
                end_date = utils.from_timestamp(anime_data["end_date"])

                anime = Anime(
                    **{
                        "episodes_released": anime_data["episodes_released"],
                        "year": start_date.year if start_date else None,
                        "episodes_total": anime_data["episodes_total"],
                        "media_type": anime_data["media_type"],
                        "content_id": anime_data["content_id"],
                        "scored_by": anime_data["scored_by"],
                        "title_en": anime_data["title_en"],
                        "title_ja": anime_data["title_ja"],
                        "title_ua": anime_data["title_ua"],
                        "status": anime_data["status"],
                        "season": anime_data["season"],
                        "score": anime_data["score"],
                        "poster_relation": image,
                        "start_date": start_date,
                        "needs_update": True,
                        "end_date": end_date,
                        "updated": updated,
                        "slug": slug,
                    }
                )

                add_anime.append(anime)

                print(f"Added anime: {anime.title_ja}")

        session.add_all(add_anime)
        await session.commit()


async def aggregator_anime():
    data = await requests.get_anime(1)
    pages = data["pagination"]["pages"]

    semaphore = asyncio.Semaphore(20)
    tasks = [make_request(semaphore, page) for page in range(1, pages + 1)]

    result = await asyncio.gather(*tasks)

    data = [item for sublist in result for item in sublist]

    for data_chunk in utils.chunkify(data, 20000):
        await save_anime_list(data_chunk)
