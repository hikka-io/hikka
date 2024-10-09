from client_requests import request_manga_random
from fastapi import status


async def test_manga_random(
    client,
    aggregator_genres,
    aggregator_companies,
    aggregator_manga,
    aggregator_manga_info,
):
    # Make request for random manga
    response = await request_manga_random(client)
    assert response.status_code == status.HTTP_200_OK
