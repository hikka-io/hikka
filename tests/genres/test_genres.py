from client_requests import request_genres
from fastapi import status


async def test_genres(client, aggregator_genres):
    # Test for list of genres
    response = await request_genres(client)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 76
