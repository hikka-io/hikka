from app.database import sessionmanager
from app import aggregator
from app import constants
from . import requests
from app import utils


async def aggregator_franchises():
    data = await requests.get_all_pages(requests.get_franchises)

    for data_chunk in utils.chunkify(data, constants.ALCHEMY_CHUNK_LIMIT):
        async with sessionmanager.session() as session:
            await aggregator.save_franchises_list(session, data_chunk)
