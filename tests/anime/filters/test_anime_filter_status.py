from client_requests import request_anime_search
from fastapi import status


async def test_anime_filter_status(client, aggregator_anime):
    # Get anime with ongoing status
    response = await request_anime_search(client, {"status": ["ongoing"]})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["status"] == "ongoing"

    # Get anime with finished status
    response = await request_anime_search(client, {"status": ["finished"]})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 12
    assert response.json()["list"][0]["status"] == "finished"

    # Get anime with both ongoing and finished statuses
    response = await request_anime_search(
        client, {"status": ["ongoing", "finished"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 12
    assert response.json()["list"][0]["status"] == "finished"
    assert response.json()["list"][4]["status"] == "ongoing"

    # Check for bad status
    response = await request_anime_search(client, {"status": ["bad"]})

    assert response.json()["code"] == "validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST
