from app.database import sessionmanager
from app import aggregator
from . import requests
from app import utils
import asyncio


async def make_request(semaphore, page):
    async with semaphore:
        data = await requests.get_anime_franchises(page)
        return data["list"]


async def save_anime_franchises_list(data):
    async with sessionmanager.session() as session:
        await aggregator.save_anime_franchises_list(session, data)


async def aggregator_anime_franchises():
    data = await requests.get_anime_franchises(1)
    pages = data["pagination"]["pages"]

    semaphore = asyncio.Semaphore(5)
    tasks = [make_request(semaphore, page) for page in range(1, pages + 1)]

    result = await asyncio.gather(*tasks)

    data = [item for sublist in result for item in sublist]

    for data_chunk in utils.chunkify(data, 20000):
        await save_anime_franchises_list(data_chunk)
