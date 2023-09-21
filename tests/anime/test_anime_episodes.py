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
    assert len(response.json()["list"]) == 15

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
    assert response.json()["pagination"]["pages"] == 2
    assert response.json()["pagination"]["page"] == 2

    # Check episode indexes and names on second page
    assert response.json()["list"][0]["index"] == 16
    assert response.json()["list"][0]["title_en"] == "What To Do Now"

    assert response.json()["list"][8]["index"] == 24
    assert response.json()["list"][8]["title_en"] == "Mercy"
