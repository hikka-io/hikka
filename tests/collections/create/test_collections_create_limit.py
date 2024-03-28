from client_requests import request_create_collection
from app.models import Collection
from datetime import datetime
from fastapi import status
from app import constants


async def test_collections_create_limit(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    collections_limit = 1000
    now = datetime.utcnow()

    for step in range(0, collections_limit + 1):
        test_session.add(
            Collection(
                **{
                    "private": False,  # ToDo: remove me
                    "content_type": "anime",
                    "labels_order": ["Good", "Great"],
                    "description": "Description",
                    "visibility": constants.COLLECTION_PUBLIC,
                    "entries": 0,
                    "spoiler": False,
                    "title": f"Test collection {step}",
                    "nsfw": False,
                    "tags": ["romance", "comedy"],
                    "deleted": False,
                    "vote_score": 0,
                    "author": create_test_user,
                    "created": now,
                    "updated": now,
                }
            )
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
