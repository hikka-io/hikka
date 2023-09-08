from client_requests import request_anime_search
from fastapi import status


async def test_anime_filter_source(
    client,
    aggregator_anime,
    aggregator_anime_info,
):
    # Get anime with original source
    response = await request_anime_search(client, {"source": ["original"]})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["source"] == "original"

    # Get anime with visual_novel source
    response = await request_anime_search(client, {"source": ["visual_novel"]})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 3
    assert response.json()["list"][0]["source"] == "visual_novel"

    # Get anime with both visual_novel and original sources
    response = await request_anime_search(
        client, {"source": ["visual_novel", "original"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 4
    assert response.json()["list"][0]["source"] == "visual_novel"
    assert response.json()["list"][1]["source"] == "original"

    # Test for bad source
    response = await request_anime_search(client, {"source": ["bad"]})

    assert response.json()["code"] == "validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
