from client_requests import request_create_collection
from client_requests import request_update_collection
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_collections_update_moderator(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user_moderator,
    get_dummy_token,
    get_test_token,
    test_session,
):
    response = await request_create_collection(
        client,
        get_dummy_token,
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

    collection_reference = response.json()["reference"]

    response = await request_update_collection(
        client,
        collection_reference,
        get_test_token,
        {
            "title": "Test collection 2",
            "tags": ["comedy", "romance"],
            "content_type": "anime",
            "description": "Description 2",
            "labels_order": ["Good", "Great"],
            "private": True,
            "spoiler": True,
            "nsfw": True,
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

    from pprint import pprint

    pprint(response.json())

    # assert response.status_code == status.HTTP_200_OK

    # # Check log
    # log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    # assert log.log_type == constants.LOG_COLLECTION_UPDATE
    # assert log.user == create_test_user_moderator
