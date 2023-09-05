from client_requests import request_anime_search
from fastapi import status


async def test_anime_filter_sort(client, aggregator_anime):
    # Check for desc sort
    response = await request_anime_search(client, {"sort": ["score:desc"]})

    assert response.status_code == status.HTTP_200_OK

    assert (
        response.json()["list"][0]["score"]
        > response.json()["list"][11]["score"]
    )

    # Check for asc sort
    response = await request_anime_search(client, {"sort": ["scored_by:asc"]})

    assert response.status_code == status.HTTP_200_OK

    assert (
        response.json()["list"][0]["scored_by"]
        < response.json()["list"][11]["scored_by"]
    )

    # Check for bad sort field
    response = await request_anime_search(client, {"sort": ["bad_field:asc"]})

    assert response.json()["code"] == "validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Check for bad sort value
    response = await request_anime_search(client, {"sort": ["scored_by:bad"]})

    assert response.json()["code"] == "validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
