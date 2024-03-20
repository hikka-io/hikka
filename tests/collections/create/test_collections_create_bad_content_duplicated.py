from client_requests import request_create_collection
from fastapi import status
from app import constants


async def test_collections_create_bad_content_duplicated(
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
            "description": "Description",
            "title": "Test collection",
            "content_type": "anime",
            "visibility": constants.COLLECTION_PUBLIC,
            "labels_order": [],
            "spoiler": False,
            "nsfw": False,
            "tags": [],
            "content": [
                {
                    "slug": "fullmetal-alchemist-brotherhood-fc524a",
                    "comment": None,
                    "label": None,
                    "order": 1,
                },
                {
                    "slug": "fullmetal-alchemist-brotherhood-fc524a",
                    "comment": None,
                    "label": None,
                    "order": 2,
                },
            ],
        },
    )

    # Make sure we got correct response code
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:bad_content"
