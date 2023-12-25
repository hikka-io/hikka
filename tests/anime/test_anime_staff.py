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
            "name_en": "Original Creator",
            "name_ua": "Автор оригіналу",
            "slug": "original-creator",
        },
    ]

    assert response.json()["list"][0]["person"]["slug"] == "aki-hamaji-dc0d68"

    # Check last staff member (on first page)
    assert response.json()["list"][11]["roles"] == [
        {
            "name_en": "Theme Song Performance",
            "name_ua": "Виконання головної музичної теми",
            "slug": "theme-song-performance",
        }
    ]

    assert (
        response.json()["list"][11]["person"]["slug"]
        == "sayumi-suzushiro-279935"
    )
