from client_requests import request_anime_franchise
from fastapi import status


async def test_anime_franchise(
    client,
    aggregator_anime,
    aggregator_anime_franchises,
):
    response = await request_anime_franchise(
        client, "shingeki-no-kyojin-0cf69a"
    )

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["list"]) == 7

    assert (
        response.json()["list"][0]["slug"]
        == "shingeki-no-kyojin-the-final-season-kanketsu-hen-833be1"
    )
    assert response.json()["list"][0]["year"] == 2023

    assert response.json()["list"][6]["slug"] == "shingeki-no-kyojin-0cf69a"
    assert response.json()["list"][6]["year"] == 2013


async def test_anime_recommendations_bad(
    client,
    aggregator_anime,
):
    response = await request_anime_franchise(client, "bad-slug")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "anime_not_found"
