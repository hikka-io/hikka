from client_requests import request_anime_recommendations
from fastapi import status


async def test_anime_recommendations(
    client,
    aggregator_anime,
    aggregator_anime_info,
):
    # Check recommendations for given anime
    response = await request_anime_recommendations(
        client, "shingeki-no-kyojin-0cf69a"
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 2

    # Check recommended anime slugs
    assert (
        response.json()["list"][0]["slug"]
        == "fullmetal-alchemist-brotherhood-fc524a"
    )
    assert response.json()["list"][1]["slug"] == "steinsgate-f29797"


async def test_anime_recommendations_bad(
    client,
    aggregator_anime,
):
    # Bad slug show throw error
    response = await request_anime_recommendations(client, "bad-slug")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "anime_not_found"
