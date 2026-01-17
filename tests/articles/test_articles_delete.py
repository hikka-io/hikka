from client_requests import request_create_article
from client_requests import request_delete_article
from client_requests import request_upload
from sqlalchemy import select, desc
from app.models import Log, Image
from fastapi import status
from app import constants


async def test_articles_delete(
    client,
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
                    "type": "image_group",
                    "children": [
                        {
                            "type": "image",
                            "url": new_attachment_url,
                            "children": [],
                        }
                    ],
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

    response = await request_delete_article(
        client, article_slug, get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True

    image = await test_session.scalar(
        select(Image).filter(
            Image.path == new_attachment_url.replace(constants.CDN_ENDPOINT, "")
        )
    )

    assert image.attachment_content_type == None  # noqa: E711
    assert image.attachment_content_id == None  # noqa: E711
    assert image.deletion_request is True

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_ARTICLE_DELETE
    assert log.user == create_test_user


async def test_articles_delete_admin(
    client,
    create_test_user_admin,
    create_dummy_user,
    get_test_token,
    get_dummy_token,
    test_session,
):
    response = await request_create_article(
        client,
        get_dummy_token,
        {
            "document": [{"text": "Lorem ipsum dor sit amet."}],
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
    assert log.user == create_test_user_admin
