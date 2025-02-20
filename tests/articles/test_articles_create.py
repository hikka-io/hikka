from client_requests import request_create_article
from client_requests import request_upload
from app.models import Article, Image, Log
from sqlalchemy import select, desc
from fastapi import status
from app import constants


async def test_articles_create(
    client,
    aggregator_anime,
    aggregator_anime_info,
    mock_s3_upload_file,
    create_test_user,
    get_test_token,
    test_session,
):
    with open("tests/data/upload/test.jpg", mode="rb") as file:
        response = await request_upload(
            client, "attachment", get_test_token, file
        )

        assert response.status_code == status.HTTP_200_OK
        assert "url" in response.json()

        new_attachment_url = response.json()["url"]

    response = await request_create_article(
        client,
        get_test_token,
        {
            "document": [
                {"text": "Lorem ipsum dor sit amet."},
                {
                    "type": "media",
                    "children": [
                        {
                            "type": "image",
                            "url": new_attachment_url,
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

    r_data = response.json()

    assert r_data["slug"].startswith("interesting-title-")
    assert r_data["document"] == [
        {"text": "Lorem ipsum dor sit amet."},
        {
            "type": "media",
            "children": [
                {
                    "type": "image",
                    "url": new_attachment_url,
                }
            ],
        },
    ]

    assert r_data["title"] == "Interesting title"
    assert len(r_data["tags"]) == 2

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_ARTICLE_CREATE
    assert log.user == create_test_user

    assert log.data["document"] == [
        {"text": "Lorem ipsum dor sit amet."},
        {
            "type": "media",
            "children": [
                {
                    "type": "image",
                    "url": new_attachment_url,
                }
            ],
        },
    ]

    assert log.data["title"] == "Interesting title"
    assert log.data["content_type"] == "anime"
    assert log.data["slug"] == r_data["slug"]
    assert log.data["category"] == "news"
    assert log.data["trusted"] is False
    assert log.data["trusted"] is False
    assert log.data["draft"] is False
    assert len(log.data["tags"]) == 2

    image = await test_session.scalar(
        select(Image).filter(
            Image.path == new_attachment_url.replace(constants.CDN_ENDPOINT, "")
        )
    )

    article = await test_session.scalar(
        select(Article).filter(Article.slug == r_data["slug"])
    )

    assert image.attachment_content_type == constants.CONTENT_ARTICLE
    assert image.attachment_content_id == article.id
