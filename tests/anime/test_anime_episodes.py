from client_requests import request_anime_episodes
from fastapi import status


async def test_anime_episodes(
    client,
    aggregator_anime,
    aggregator_anime_info,
):
    # Get episodes for first season of SNK
    response = await request_anime_episodes(client, "shingeki-no-kyojin-0cf69a")

    assert response.status_code == status.HTTP_200_OK

    # Check pagination data
    assert response.json()["pagination"]["total"] == 25
    assert len(response.json()["list"]) == 12

    # Check episode indexes and names
    assert response.json()["list"][0]["index"] == 1
    assert (
        response.json()["list"][0]["title_en"]
        == "To You Two Thousand Years Later"
    )

    assert response.json()["list"][11]["index"] == 12
    assert response.json()["list"][11]["title_en"] == "Wound"


async def test_anime_episodes_pagination(
    client,
    aggregator_anime,
    aggregator_anime_info,
):
    # Check second page
    response = await request_anime_episodes(
        client, "shingeki-no-kyojin-0cf69a", 2
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["pagination"]["total"] == 25
    assert response.json()["pagination"]["pages"] == 3
    assert response.json()["pagination"]["page"] == 2

    # Check episode indexes and names on second page
    assert response.json()["list"][0]["index"] == 13
    assert response.json()["list"][0]["title_en"] == "Primordial Desire"

    assert response.json()["list"][11]["index"] == 24
    assert response.json()["list"][11]["title_en"] == "Mercy"


async def test_anime_episodes_bad(
    client,
    aggregator_anime,
):
    # Bad slug show throw error
    response = await request_anime_episodes(client, "bad-slug")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "anime_not_found"
