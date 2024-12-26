from client_requests import request_create_article
from client_requests import request_update_article
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_articles_update(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    response = await request_create_article(
        client,
        get_test_token,
        {
            "cover": None,
            "text": "Lorem ipsum dor sit amet.",
            "title": "Interesting title",
            "tags": ["interesting", "tag"],
            "category": "news",
            "content": {
                "content_type": "anime",
                "slug": "fullmetal-alchemist-brotherhood-fc524a",
            },
            "draft": False,
            "trusted": False,
        },
    )

    # Make sure we got correct response code
    assert response.status_code == status.HTTP_200_OK

    article_slug = response.json()["slug"]

    response = await request_update_article(
        client,
        article_slug,
        get_test_token,
        {
            "cover": None,
            "text": "Amet sit dor ipsum lorem.",
            "title": "Amazing title",
            "tags": ["wow", "tag"],
            "category": "news",
            "content": {
                "content_type": "anime",
                "slug": "bocchi-the-rock-9e172d",
            },
            "draft": True,
            "trusted": False,
        },
    )

    # Let's check status again
    assert response.status_code == status.HTTP_200_OK

    r_data = response.json()

    assert r_data["text"] == "Amet sit dor ipsum lorem."
    assert r_data["title"] == "Amazing title"

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_ARTICLE_UPDATE
    assert log.user == create_test_user

    assert set(log.data["before"]["tags"]) != set(log.data["after"]["tags"])
    assert log.data["before"]["content_id"] != log.data["after"]["content_id"]
    assert log.data["before"]["title"] != log.data["after"]["title"]
    assert log.data["before"]["draft"] != log.data["after"]["draft"]
    assert log.data["before"]["text"] != log.data["after"]["text"]
