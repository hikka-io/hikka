from client_requests import request_anime_characters
from fastapi import status


async def test_anime_characters(
    client,
    aggregator_characters,
    aggregator_anime,
    aggregator_anime_info,
):
    response = await request_anime_characters(client, "bocchi-the-rock-9e172d")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 17
    assert len(response.json()["list"]) == 12

    # Check first character
    assert response.json()["list"][0]["main"] is True
    assert (
        response.json()["list"][0]["character"]["slug"] == "hitori-gotou-cadd70"
    )

    # Check last character (on first page)
    assert response.json()["list"][11]["main"] is False
    assert (
        response.json()["list"][11]["character"]["slug"]
        == "shima-iwashita-a22b1e"
    )
