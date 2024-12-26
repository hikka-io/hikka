from client_requests import request_create_article
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_articles_create(
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

    r_data = response.json()

    assert r_data["slug"].startswith("interesting-title-")
    assert len(r_data["tags"]) == 2

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_ARTICLE_CREATE
    assert log.user == create_test_user

    assert log.data["text"] == "Lorem ipsum dor sit amet."
    assert log.data["title"] == "Interesting title"
    assert log.data["content_type"] == "anime"
    assert log.data["slug"] == r_data["slug"]
    assert log.data["category"] == "news"
    assert log.data["trusted"] is False
    assert log.data["trusted"] is False
    assert log.data["draft"] is False
    assert len(log.data["tags"]) == 2
    assert log.data["cover"] is None
