from app.models import Anime, AnimeFranchise
from app.database import sessionmanager
from sqlalchemy import select
from . import requests
from app import utils
import asyncio


async def make_request(semaphore, page):
    async with semaphore:
        data = await requests.get_anime_franchises(page)
        return data["list"]


# ToDo: optimize it
async def save_anime_franchises_list(data):
    async with sessionmanager.session() as session:
        content_ids = [entry["content_id"] for entry in data]

        cache = await session.scalars(
            select(AnimeFranchise).where(
                AnimeFranchise.content_id.in_(content_ids)
            )
        )

        franchises_cache = {entry.content_id: entry for entry in cache}

        for franchise_data in data:
            if not (
                franchise := franchises_cache.get(franchise_data["content_id"])
            ):
                franchise = AnimeFranchise(
                    content_id=franchise_data["content_id"]
                )

            updated = utils.from_timestamp(franchise_data["updated"])

            if updated == franchise.updated:
                continue

            franchise.scored_by = franchise_data["scored_by"]
            franchise.score = franchise_data["score"]
            franchise.updated = updated

            session.add(franchise)
            await session.commit()

            cache = await session.scalars(
                select(Anime).where(
                    Anime.content_id.in_(franchise_data["franchise_entries"])
                )
            )

            update_anime = []

            for anime in cache:
                anime.franchise_relation = franchise
                update_anime.append(anime)

            session.add_all(update_anime)

            print("Processed franchise " + franchise_data["content_id"])

        await session.commit()


async def aggregator_anime_franchises():
    data = await requests.get_anime_franchises(1)
    pages = data["pagination"]["pages"]

    semaphore = asyncio.Semaphore(20)
    tasks = [make_request(semaphore, page) for page in range(1, pages + 1)]

    result = await asyncio.gather(*tasks)

    data = [item for sublist in result for item in sublist]

    for data_chunk in utils.chunkify(data, 20000):
        await save_anime_franchises_list(data_chunk)
