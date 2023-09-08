from client_requests import request_characters_anime
from fastapi import status


async def test_characters_anime(
    client,
    aggregator_characters,
    aggregator_anime,
    aggregator_anime_info,
):
    # Get anime where character has starred
    response = await request_characters_anime(client, "levi-565409")

    assert response.status_code == status.HTTP_200_OK

    # Check slugs
    assert (
        response.json()["list"][0]["anime"]["slug"]
        == "shingeki-no-kyojin-season-3-part-2-91a350"
    )

    assert (
        response.json()["list"][6]["anime"]["slug"]
        == "shingeki-no-kyojin-season-2-b88bf4"
    )
