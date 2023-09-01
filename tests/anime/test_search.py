from client_requests import request_anime_search
from fastapi import status


async def test_anime_search(client, aggregator_anime):
    response = await request_anime_search(client)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 5


# ToDo: filters
# ToDo: pagination
