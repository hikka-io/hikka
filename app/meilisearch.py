from meilisearch_python_async.errors import MeilisearchError
from meilisearch_python_async import Client
from app.utils import pagination_dict
from app.errors import Abort
from app import constants
import config


async def search(
    content_index,
    query=None,
    sort=None,
    page=None,
    filter=None,
    hits_per_page=constants.SEARCH_RESULT_LIMIT,
):
    try:
        async with Client(**config.meilisearch) as client:
            index = client.index(content_index)

            result = await index.search(
                hits_per_page=hits_per_page,
                filter=filter,
                query=query,
                sort=sort,
                page=page,
            )

            return {
                "pagination": pagination_dict(
                    result.total_hits, result.page, result.hits_per_page
                ),
                "list": result.hits,
            }

    except MeilisearchError:
        raise Abort("search", "query-down")
