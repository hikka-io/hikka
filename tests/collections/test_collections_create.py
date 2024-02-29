from client_requests import request_create_collection
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


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

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_COLLECTION_CREATE
    assert log.user == create_test_user

    assert log.data["labels_order"] == ["Good", "Great"]
    assert log.data["tags"] == ["romance", "comedy"]
    assert log.data["description"] == "Description"
    assert log.data["title"] == "Test collection"
    assert log.data["content_type"] == "anime"
    assert log.data["private"] is False
    assert log.data["spoiler"] is False
    assert log.data["nsfw"] is False

    assert len(log.data["content"]) == 2

    assert log.data["content"][0]["comment"] is None
    assert log.data["content"][0]["content_type"] == "anime"
    assert log.data["content"][0]["label"] == "Good"
    assert log.data["content"][0]["order"] == 1

    assert log.data["content"][1]["comment"] == "Author comment"
    assert log.data["content"][1]["content_type"] == "anime"
    assert log.data["content"][1]["label"] == "Great"
    assert log.data["content"][1]["order"] == 2
