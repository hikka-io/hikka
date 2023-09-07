from client_requests import request_anime_search
from fastapi import status


# producers
# studios
# genres


async def test_anime_filter_producers(
    client,
    aggregator_companies,
    aggregator_anime,
    aggregator_anime_info,
):
    response = await request_anime_search(
        client, {"producers": ["aniplex-332844"]}
    )

    assert len(response.json()["list"]) == 5


# async def test_anime_filter_studios():
#     response = await request_anime_search(client, {})


# async def test_anime_filter_genres():
#     response = await request_anime_search(client, {})
