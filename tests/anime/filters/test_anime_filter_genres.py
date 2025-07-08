from client_requests import request_anime_search
from fastapi import status


async def test_anime_filter_genres(
    client,
    aggregator_genres,
    aggregator_anime,
    aggregator_anime_info,
):
    # Check for anime with ALL specified genres (e.g., action, drama, and military)
    response = await request_anime_search(
        client, {"genres": ["action", "drama", "military"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 7

    # When we try to get anime with both adventure and comedy genres
    # It should return empty list because both genres must be present
    response = await request_anime_search(
        client, {"genres": ["adventure", "comedy"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 0

    # Check for simple exclusion: include action/drama, exclude fantasy
    # The same 7 anime should be found, as they don't have the 'fantasy' genre.
    response = await request_anime_search(
        client, {"genres": ["action", "drama", "-fantasy"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 7

    # Check core exclusion: include action/drama, but EXCLUDE military
    # This should now exclude the 7 anime found earlier, resulting in an empty list.
    response = await request_anime_search(
        client, {"genres": ["action", "drama", "-military"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1

    # Check contradictory filter: include and exclude the same genre
    # This is a valid query but should always return an empty list.
    response = await request_anime_search(
        client, {"genres": ["action", "-action"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 0

    # Check for an unknown genre (without prefix)
    response = await request_anime_search(client, {"genres": ["bad-genre"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "anime:unknown_genre"

    # Check for an unknown genre (with exclusion prefix)
    response = await request_anime_search(client, {"genres": ["-bad-genre"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "anime:unknown_genre"