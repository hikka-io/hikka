from client_requests import request_create_article
from client_requests import request_update_article
from client_requests import request_upload
from fastapi import status


async def test_articles_cover(
    client,
    create_test_user,
    get_test_token,
    mock_s3_upload_file,
    test_session,
):
    with open("tests/data/upload/test.jpg", mode="rb") as file:
        response = await request_upload(
            client, "attachment", get_test_token, file
        )

        assert response.status_code == status.HTTP_200_OK
        assert "url" in response.json()

        attachment_url = response.json()["url"]

    response = await request_create_article(
        client,
        get_test_token,
        {
            "cover": attachment_url,
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
    assert response.json()["cover"] == attachment_url

    article_slug = response.json()["slug"]

    with open("tests/data/upload/test.jpg", mode="rb") as file:
        response = await request_upload(
            client, "attachment", get_test_token, file
        )

        assert response.status_code == status.HTTP_200_OK
        assert "url" in response.json()

        new_attachment_url = response.json()["url"]

    # Just in case
    assert new_attachment_url != attachment_url

    response = await request_update_article(
        client,
        article_slug,
        get_test_token,
        {
            "cover": new_attachment_url,
            "text": "Lorem ipsum dor sit amet.",
            "title": "Interesting title",
            "tags": ["interesting", "tag"],
            "category": "news",
            "content": None,
            "draft": False,
            "trusted": False,
        },
    )

    # Let's check status again
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["cover"] == new_attachment_url


async def test_articles_cover_moderator(
    client,
    create_test_user_moderator,
    create_dummy_user,
    get_test_token,
    get_dummy_token,
    mock_s3_upload_file,
    test_session,
):
    with open("tests/data/upload/test.jpg", mode="rb") as file:
        response = await request_upload(
            client, "attachment", get_dummy_token, file
        )

        assert response.status_code == status.HTTP_200_OK
        assert "url" in response.json()

        attachment_url = response.json()["url"]

    response = await request_create_article(
        client,
        get_dummy_token,
        {
            "cover": attachment_url,
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
    assert response.json()["cover"] == attachment_url

    article_slug = response.json()["slug"]

    with open("tests/data/upload/test.jpg", mode="rb") as file:
        response = await request_upload(
            client, "attachment", get_test_token, file
        )

        assert response.status_code == status.HTTP_200_OK
        assert "url" in response.json()

        new_attachment_url = response.json()["url"]

    # Just in case
    assert new_attachment_url != attachment_url

    response = await request_update_article(
        client,
        article_slug,
        get_test_token,
        {
            "cover": new_attachment_url,
            "text": "Lorem ipsum dor sit amet.",
            "title": "Interesting title",
            "tags": ["interesting", "tag"],
            "category": "news",
            "content": None,
            "draft": False,
            "trusted": False,
        },
    )

    # Let's check status again
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["cover"] == new_attachment_url
