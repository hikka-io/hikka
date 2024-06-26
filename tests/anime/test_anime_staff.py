from client_requests import request_anime_staff
from fastapi import status


async def test_anime_staff(
    client,
    aggregator_anime_roles: None,
    aggregator_people: None,
    aggregator_anime: None,
    aggregator_anime_info: None,
):
    response = await request_anime_staff(client, "bocchi-the-rock-9e172d")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 19
    assert len(response.json()["list"]) == 15

    # Check first staff member
    assert response.json()["list"][0]["weight"] == 1080
    assert (
        response.json()["list"][0]["person"]["slug"]
        == "keiichirou-saitou-c38cac"
    )

    # Check last staff member (on first page)
    assert response.json()["list"][11]["weight"] == 80
    assert (
        response.json()["list"][11]["person"]["slug"] == "tomoki-kikuya-e4348e"
    )
