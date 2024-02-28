from client_requests import request_create_collection

# from sqlalchemy import select, desc, func
# from app.models import Log
from fastapi import status

# from app import constants


async def test_collections_create(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    response = await request_create_collection(
        client,
        get_test_token,
        {
            "title": "Test collection",
            "tags": ["romance", "comedy"],
            "content_type": "anime",
            "description": "Description",
            "labels_order": ["Good", "Great"],
            "private": False,
            "spoiler": False,
            "nsfw": False,
            "content": [
                {
                    "slug": "fullmetal-alchemist-brotherhood-fc524a",
                    "comment": None,
                    "label": "Good",
                    "order": 1,
                },
                {
                    "slug": "bocchi-the-rock-9e172d",
                    "comment": "Author comment",
                    "label": "Great",
                    "order": 2,
                },
            ],
        },
    )

    # Make sure we got correct response code
    assert response.status_code == status.HTTP_200_OK

    assert response.json()["content_type"] == "anime"
    assert response.json()["entries"] == 2

    assert len(response.json()["collection"]) == 2

    assert response.json()["collection"][0]["order"] == 1
    assert (
        response.json()["collection"][0]["content"]["slug"]
        == "fullmetal-alchemist-brotherhood-fc524a"
    )

    assert response.json()["collection"][1]["order"] == 2
    assert (
        response.json()["collection"][1]["content"]["slug"]
        == "bocchi-the-rock-9e172d"
    )
