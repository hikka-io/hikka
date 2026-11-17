from app.database import sessionmanager
from app import aggregator
from app import constants
from . import requests
from app import utils


async def aggregator_characters():
    data = await requests.get_all_pages(requests.get_characters)

    for data_chunk in utils.chunkify(data, constants.ALCHEMY_CHUNK_LIMIT):
        async with sessionmanager.session() as session:
            await aggregator.save_characters(session, data_chunk)
