from sqlalchemy.ext.asyncio.session import AsyncSession
from async_asgi_testclient.testing import TestClient
from client_requests import request_create_article
from client_requests import request_update_article
from unittest.mock import AsyncMock, MagicMock
from client_requests import request_upload
from app.models.user.user import User
from app.models import Image, Article
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants
from typing import Any


async def test_articles_update(
    client: TestClient,
    aggregator_anime: None,
    aggregator_anime_info: None,
    mock_s3_upload_file: MagicMock | AsyncMock,
    create_test_user: Any,
    get_test_token: Any,
    test_session: AsyncSession,
):
    with open("tests/data/upload/test.jpg", mode="rb") as file:
        response = await request_upload(
            client, "attachment", get_test_token, file
        )

        assert response.status_code == status.HTTP_200_OK
        assert "url" in response.json()

        original_attachment_url = response.json()["url"]

    response = await request_create_article(
        client,
        get_test_token,
        {
            "document": [
                {
                    "type": "preview",
                    "children": [{"text": "Lorem ipsum dor sit amet."}],
                },
                {
                    "type": "image_group",
                    "children": [
                        {
                            "type": "image",
                            "url": original_attachment_url,
                            "children": [],
                        }
                    ],
                },
            ],
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

    # Here we check whether image has been attached to article
    article = await test_session.scalar(
        select(Article).filter(Article.slug == article_slug)
    )

    original_image = await test_session.scalar(
        select(Image).filter(
            Image.path
            == original_attachment_url.replace(constants.CDN_ENDPOINT, "")
        )
    )

    assert original_image.attachment_content_type == constants.CONTENT_ARTICLE
    assert original_image.attachment_content_id == article.id
    assert original_image.deletion_request is False

    with open("tests/data/upload/test.jpg", mode="rb") as file:
        response = await request_upload(
            client, "attachment", get_test_token, file
        )

        assert response.status_code == status.HTTP_200_OK
        assert "url" in response.json()

        updated_attachment_url = response.json()["url"]

    assert updated_attachment_url != original_attachment_url

    response = await request_update_article(
        client,
        article_slug,
        get_test_token,
        {
            "document": [
                {
                    "type": "preview",
                    "children": [{"text": "Amet sit dor ipsum lorem."}],
                },
                {
                    "type": "image_group",
                    "children": [
                        {
                            "type": "image",
                            "url": updated_attachment_url,
                            "children": [],
                        }
                    ],
                },
            ],
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

    # Here we check updated and original images
    updated_image = await test_session.scalar(
        select(Image).filter(
            Image.path
            == updated_attachment_url.replace(constants.CDN_ENDPOINT, "")
        )
    )

    assert updated_image.attachment_content_type == constants.CONTENT_ARTICLE
    assert updated_image.attachment_content_id == article.id
    assert updated_image.deletion_request is False

    await test_session.refresh(original_image)

    assert original_image.attachment_content_type == None  # noqa: E711
    assert original_image.attachment_content_id == None  # noqa: E711
    assert original_image.deletion_request is True

    r_data = response.json()

    assert r_data["document"] == [
        {
            "type": "preview",
            "children": [{"text": "Amet sit dor ipsum lorem."}],
        },
        {
            "type": "image_group",
            "children": [
                {
                    "type": "image",
                    "url": updated_attachment_url,
                    "children": [],
                }
            ],
        },
    ]

    assert r_data["title"] == "Amazing title"

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_ARTICLE_UPDATE
    assert log.user == create_test_user

    assert set(log.data["before"]["tags"]) != set(log.data["after"]["tags"])
    assert log.data["before"]["content_id"] != log.data["after"]["content_id"]
    assert log.data["before"]["title"] != log.data["after"]["title"]
    assert log.data["before"]["draft"] != log.data["after"]["draft"]
    assert log.data["before"]["document"] != log.data["after"]["document"]


async def test_articles_update_moderator(
    client: TestClient,
    create_test_user_moderator: User,
    create_dummy_user: User,
    get_test_token: Any,
    get_dummy_token: str,
    test_session: AsyncSession,
):
    response = await request_create_article(
        client,
        get_dummy_token,
        {
            "document": [
                {
                    "type": "preview",
                    "children": [{"text": "Lorem ipsum dor sit amet."}],
                },
            ],
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

    response = await request_update_article(
        client,
        article_slug,
        get_test_token,
        {
            "document": [
                {
                    "type": "preview",
                    "children": [{"text": "Amet sit dor ipsum lorem."}],
                },
            ],
            "title": "Amazing title",
            "tags": ["wow", "tag"],
            "category": "news",
            "content": None,
            "draft": True,
            "trusted": False,
        },
    )

    # Let's check status again
    assert response.status_code == status.HTTP_200_OK

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_ARTICLE_UPDATE
    assert log.user == create_test_user_moderator
