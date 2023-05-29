from app.models import Anime, AnimeFranchise
from app.database import sessionmanager
from sqlalchemy import select
from . import requests
from app import utils
import asyncio
import config


async def make_request(semaphore, page):
    async with semaphore:
        data = await requests.get_anime_franchises(page)
        return data["list"]


# ToDo: optimize it
async def save_anime_franchises_list(data):
    sessionmanager.init(config.database)

    async with sessionmanager.session() as session:
        for franchise_data in data:
            if not (
                franchise := await session.scalar(
                    select(AnimeFranchise).filter_by(
                        content_id=franchise_data["reference"]
                    )
                )
            ):
                franchise = AnimeFranchise(
                    content_id=franchise_data["reference"]
                )

            franchise.updated = utils.from_timestamp(franchise_data["updated"])
            franchise.scored_by = franchise_data["scored_by"]
            franchise.score = franchise_data["score"]

            session.add(franchise)
            await session.commit()

            cache = await session.scalars(
                select(Anime).where(
                    Anime.content_id.in_(franchise_data["anime"])
                )
            )

            update_anime = []

            for anime in cache:
                anime.franchise = franchise
                update_anime.append(anime)

            session.add_all(update_anime)
            await session.commit()

            print("Processed franchise " + franchise_data["name"])


async def aggregator_anime_franchises():
    data = await requests.get_anime_franchises(1)
    pages = data["pagination"]["pages"]

    semaphore = asyncio.Semaphore(20)
    tasks = [make_request(semaphore, page) for page in range(1, pages + 1)]

    result = await asyncio.gather(*tasks)

    data = [item for sublist in result for item in sublist]

    for data_chunk in utils.chunkify(data, 20000):
        await save_anime_franchises_list(data_chunk)
