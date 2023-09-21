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
    assert response.json()["list"][0]["roles"] == [
        {
            "name_en": "Producer",
            "name_ua": None,
            "slug": "producer",
        },
    ]

    assert (
        response.json()["list"][0]["person"]["slug"] == "shouta-umehara-fc94cf"
    )

    # Check last staff member (on first page)
    assert response.json()["list"][11]["roles"] == [
        {
            "name_en": "Theme Song Performance",
            "name_ua": None,
            "slug": "theme-song-performance",
        }
    ]

    assert (
        response.json()["list"][11]["person"]["slug"]
        == "sayumi-suzushiro-279935"
    )
