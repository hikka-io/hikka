from client_requests import request_create_article
from client_requests import request_delete_article
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_articles_delete(
    client,
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
            "content": None,
            "draft": False,
            "trusted": False,
        },
    )

    # Make sure we got correct response code
    assert response.status_code == status.HTTP_200_OK

    article_slug = response.json()["slug"]

    response = await request_delete_article(
        client, article_slug, get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_ARTICLE_DELETE
    assert log.user == create_test_user


async def test_articles_delete_moderator(
    client,
    create_test_user_moderator,
    create_dummy_user,
    get_test_token,
    get_dummy_token,
    test_session,
):
    response = await request_create_article(
        client,
        get_dummy_token,
        {
            "cover": None,
            "text": "Lorem ipsum dor sit amet.",
            "title": "Interesting title",
            "tags": ["interesting", "tag"],
            "category": "news",
            "content": None,
            "draft": False,
            "trusted": False,
        },
    )

    # Make sure we got correct response code
    assert response.status_code == status.HTTP_200_OK

    article_slug = response.json()["slug"]

    response = await request_delete_article(
        client, article_slug, get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_ARTICLE_DELETE
    assert log.user == create_test_user_moderator
