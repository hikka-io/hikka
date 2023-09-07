from client_requests import request_anime_search
from fastapi import status


async def test_anime_filter_genres(
    client,
    aggregator_anime_genres,
    aggregator_anime,
    aggregator_anime_info,
):
    # Check anime with adventure genre
    response = await request_anime_search(client, {"genres": ["adventure"]})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1

    # Check anime with adventure comedy
    response = await request_anime_search(client, {"genres": ["comedy"]})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1

    # When we try to get anime with both adventure and comedy genres
    # It should return empty list because both genres must be present
    response = await request_anime_search(
        client, {"genres": ["adventure", "comedy"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 0

    # Now let's try to get anime with action, drama and military genres (SNK)
    response = await request_anime_search(
        client, {"genres": ["action", "drama", "military"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 7

    # And one last test to make sure only correct genres can be used
    response = await request_anime_search(client, {"genres": ["bad-genre"]})

    assert response.json()["code"] == "anime_unknown_genre"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
