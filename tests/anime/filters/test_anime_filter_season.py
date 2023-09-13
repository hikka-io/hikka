from client_requests import request_anime_search
from fastapi import status


async def test_anime_filter_season(client, aggregator_anime):
    # Get anime with fall season
    response = await request_anime_search(client, {"season": ["fall"]})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 2
    assert response.json()["list"][0]["season"] == "fall"

    # Get anime with summer season
    response = await request_anime_search(client, {"season": ["summer"]})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 2
    assert response.json()["list"][0]["season"] == "summer"

    # Get anime with both summer and fall seasons
    response = await request_anime_search(
        client, {"season": ["summer", "fall"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 4
    assert response.json()["list"][0]["season"] == "summer"
    assert response.json()["list"][1]["season"] == "fall"

    # Check for bad season
    response = await request_anime_search(client, {"season": ["bad"]})

    assert response.json()["code"] == "system:validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
