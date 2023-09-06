from client_requests import request_anime_search
from fastapi import status


async def test_anime_filter_rating(
    client,
    aggregator_anime,
    aggregator_anime_info,
):
    # Get anime with r rating
    response = await request_anime_search(client, {"rating": ["r"]})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 8
    assert response.json()["list"][0]["rating"] == "r"

    # Get anime with pg_13 rating
    response = await request_anime_search(client, {"rating": ["pg_13"]})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 7
    assert response.json()["list"][0]["rating"] == "pg_13"

    # Get anime with both special and movie media types
    response = await request_anime_search(client, {"rating": ["r", "pg_13"]})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 12
    assert response.json()["list"][0]["rating"] == "r"
    assert response.json()["list"][1]["rating"] == "pg_13"

    # ToDo: test for bad rating
