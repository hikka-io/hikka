from app.database import sessionmanager
from app import aggregator
from app import constants
from . import requests
from app import utils


async def aggregator_novel():
    data = await requests.get_all_pages(requests.get_novel)

    for data_chunk in utils.chunkify(data, constants.ALCHEMY_CHUNK_LIMIT_ALT):
        async with sessionmanager.session() as session:
            await aggregator.save_novel_list(session, data_chunk)
