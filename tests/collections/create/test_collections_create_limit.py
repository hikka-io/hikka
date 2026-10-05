from client_requests import request_create_collection
from fastapi import status
from app import constants
import helpers


async def test_collections_create_limit(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    collections_limit = 1000

    for step in range(0, collections_limit + 1):
        collection = helpers.make_collection(
            create_test_user,
            title=f"Test collection {step}",
            labels_order=["Good", "Great"],
            tags=["romance", "comedy"],
        )

        # The quota is counted by ownership, not by author_id, so the
        # membership row is what actually makes these collections count
        test_session.add_all(
            [
                collection,
                helpers.make_collection_member(
                    create_test_user,
                    collection=collection,
                    role=constants.COLLECTION_MEMBER_OWNER,
                ),
            ]
        )

    await test_session.commit()

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

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:limit"
