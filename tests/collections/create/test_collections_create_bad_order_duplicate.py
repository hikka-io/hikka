from client_requests import request_create_collection
from fastapi import status
from app import constants


async def test_collections_create_bad_order_duplicate(
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
            "labels_order": [],
            "visibility": constants.COLLECTION_PUBLIC,
            "spoiler": False,
            "nsfw": False,
            "content": [
                {
                    "slug": "fullmetal-alchemist-brotherhood-fc524a",
                    "comment": None,
                    "label": None,
                    "order": 1,
                },
                {
                    "slug": "bocchi-the-rock-9e172d",
                    "comment": "Author comment",
                    "label": None,
                    "order": 1,
                },
            ],
        },
    )

    # Make sure we got correct response code
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:bad_order_duplicated"
