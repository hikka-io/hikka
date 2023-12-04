from client_requests import request_anime_franchise
from fastapi import status


async def test_anime_franchise(
    client,
    aggregator_anime,
    aggregator_anime_franchises,
):
    # Check franchise entries for SNK
    response = await request_anime_franchise(
        client, "shingeki-no-kyojin-0cf69a"
    )

    assert response.status_code == status.HTTP_200_OK

    # One day they will finish it
    # Update: they did
    assert len(response.json()["list"]) == 7

    # Check slugs and relase dates
    assert (
        response.json()["list"][0]["slug"]
        == "shingeki-no-kyojin-the-final-season-kanketsu-hen-833be1"
    )
    assert response.json()["list"][0]["year"] == 2023

    assert response.json()["list"][6]["slug"] == "shingeki-no-kyojin-0cf69a"

    # 10 years... damn
    assert response.json()["list"][6]["year"] == 2013


async def test_anime_no_franchise(
    client,
    aggregator_anime,
    aggregator_anime_franchises,
):
    # Check franchise entries for Bocchi
    response = await request_anime_franchise(client, "bocchi-the-rock-9e172d")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "anime:no_franchise"
