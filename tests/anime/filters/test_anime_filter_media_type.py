from client_requests import request_anime_search
from fastapi import status


async def test_anime_filter_media_type(client, aggregator_anime):
    # Get anime with media type special
    response = await request_anime_search(client, {"media_type": ["special"]})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["media_type"] == "special"

    # Get anime with media type movie
    response = await request_anime_search(client, {"media_type": ["movie"]})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 2
    assert response.json()["list"][0]["media_type"] == "movie"

    # Get anime with both special and movie media types
    response = await request_anime_search(
        client, {"media_type": ["special", "movie"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 3
    assert response.json()["list"][0]["media_type"] == "special"
    assert response.json()["list"][1]["media_type"] == "movie"

    # Check for bad media type
    response = await request_anime_search(client, {"media_type": ["bad_type"]})

    assert response.json()["code"] == "system:validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
