from meilisearch_python_async.errors import MeilisearchError
from meilisearch_python_async import Client
from app.schemas import QuerySearchArgs
from app.utils import pagination_dict
from app.errors import Abort
from app import constants
import config


async def people_search(search: QuerySearchArgs):
    try:
        async with Client(**config.meilisearch) as client:
            index = client.index(constants.SEARCH_INDEX_PEOPLE)

            result = await index.search(
                hits_per_page=constants.SEARCH_RESULT_LIMIT,
                sort=["favorites:desc"],
                query=search.query,
                page=search.page,
            )

            return {
                "pagination": pagination_dict(
                    result.total_hits, result.page, result.hits_per_page
                ),
                "list": result.hits,
            }

    except MeilisearchError:
        raise Abort("search", "query-down")
