from app.database import sessionmanager
from app import aggregator
from app import constants
from . import requests
from app import utils
import asyncio


async def make_request(semaphore, page):
    async with semaphore:
        data = await requests.get_manga(page)
        return data["list"]


async def save_manga_list(data):
    async with sessionmanager.session() as session:
        await aggregator.save_manga_list(session, data)


async def aggregator_manga():
    data = await requests.get_manga(1)
    pages = data["pagination"]["pages"]

    semaphore = asyncio.Semaphore(5)
    tasks = [make_request(semaphore, page) for page in range(1, pages + 1)]

    result = await asyncio.gather(*tasks)

    data = [item for sublist in result for item in sublist]

    for data_chunk in utils.chunkify(data, constants.ALCHEMY_CHUNK_LIMIT_ALT):
        await save_manga_list(data_chunk)
