# from meilisearch_python_async.errors import MeiliSearchCommunicationError
# from meilisearch_python_async.errors import MeiliSearchApiError
from meilisearch_python_async import Client
from .schemas import AnimeSearchArgs
from app.errors import Abort
from typing import Union
import config


async def anime_search(search: AnimeSearchArgs):
    return []
