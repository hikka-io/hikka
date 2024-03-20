from client_requests import request_create_collection
from client_requests import request_update_collection
from fastapi import status
from app import constants


async def test_collections_update_bad_conten_type(
    client,
    aggregator_anime,
    aggregator_anime_info,
    aggregator_people,
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
            "visibility": constants.COLLECTION_PUBLIC,
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

    collection_reference = response.json()["reference"]

    response = await request_update_collection(
        client,
        collection_reference,
        get_test_token,
        {
            "title": "Test collection 2",
            "tags": ["comedy", "romance"],
            "content_type": "person",
            "description": "Description 2",
            "labels_order": [],
            "visibility": constants.COLLECTION_UNLISTED,
            "spoiler": True,
            "nsfw": True,
            "content": [
                {
                    "slug": "justin-cook-77f1b3",
                    "comment": None,
                    "label": None,
                    "order": 1,
                }
            ],
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:bad_content_type"
