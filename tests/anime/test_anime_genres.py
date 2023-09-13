from client_requests import request_anime_genres
from fastapi import status


async def test_anime_genres(client, aggregator_anime_genres):
    # Test for list of anime genres
    response = await request_anime_genres(client)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 76
