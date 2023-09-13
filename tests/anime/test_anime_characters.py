from client_requests import request_anime_characters
from fastapi import status


async def test_anime_characters(
    client,
    aggregator_characters,
    aggregator_anime,
    aggregator_anime_info,
):
    # Get list of anime characters
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


async def test_anime_characters_pagination(
    client,
    aggregator_characters,
    aggregator_anime,
    aggregator_anime_info,
):
    # Check second page of anime characters
    response = await request_anime_characters(
        client, "bocchi-the-rock-9e172d", 2
    )

    assert response.status_code == status.HTTP_200_OK

    # Check first character on second page
    assert response.json()["list"][0]["main"] is False
    assert (
        response.json()["list"][0]["character"]["slug"]
        == "music-store-clerk-4eb9b6"
    )

    # Check last character on second page
    assert response.json()["list"][4]["main"] is False
    assert (
        response.json()["list"][4]["character"]["slug"]
        == "ginjirou-yoshida-2f08d8"
    )
