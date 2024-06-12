from client_requests import request_anime_search
from fastapi import status


async def test_anime_only_translated(
    client,
    aggregator_genres,
    aggregator_anime,
    aggregator_anime_info,
):
    # First let's get all titles
    response = await request_anime_search(client, {"only_translated": False})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 16

    # And now only translated to Ukrainian
    response = await request_anime_search(client, {"only_translated": True})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 15
