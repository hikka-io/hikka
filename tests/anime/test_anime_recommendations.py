from client_requests import request_anime_recommendations
from fastapi import status


async def test_anime_recommendations(
    client,
    aggregator_anime,
    aggregator_anime_info,
):
    response = await request_anime_recommendations(
        client, "shingeki-no-kyojin-0cf69a"
    )

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["list"]) == 2
    assert (
        response.json()["list"][0]["slug"]
        == "fullmetal-alchemist-brotherhood-fc524a"
    )
    assert response.json()["list"][1]["slug"] == "steinsgate-f29797"
