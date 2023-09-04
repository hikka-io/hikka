from client_requests import request_anime_search
from fastapi import status


async def test_anime_filters(client, aggregator_anime):
    from pprint import pprint

    # sort
    # page
    # years
    # score
    # media_type
    # rating
    # status
    # source
    # season
    # producers
    # studios
    # genres

    response = await request_anime_search(client, {})

    pprint(response.json())
