from client_requests import request_anime_random
from fastapi import status


async def test_anime_random(
    client,
    aggregator_anime,
    aggregator_anime_info,
):

    # Make request for random anime
    response = await request_anime_random(client)
    assert response.status_code == status.HTTP_200_OK
