from client_requests import request_create_article
from client_requests import request_upload
from fastapi import status


async def test_articles_create_cover_bad_url(
    client,
    create_test_user,
    get_test_token,
    test_session,
):
    bad_attachment_url = (
        "https://cdn.hikka.io/uploads/baduser/attachment/bad.jpg"
    )

    response = await request_create_article(
        client,
        get_test_token,
        {
            "cover": bad_attachment_url,
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
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "articles:cover_not_found"


async def test_articles_create_cover_bad_image(
    client,
    create_test_user,
    get_test_token,
    mock_s3_upload_file,
    test_session,
):
    with open("tests/data/upload/test.jpg", mode="rb") as file:
        response = await request_upload(client, "avatar", get_test_token, file)
        assert response.status_code == status.HTTP_200_OK
        bad_attachment_url = response.json()["url"]

    response = await request_create_article(
        client,
        get_test_token,
        {
            "cover": bad_attachment_url,
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
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "articles:bad_cover"


async def test_articles_cover_bad_reuse(
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
            "document": [{"text": "Lorem ipsum dor sit amet."}],
            "title": "Interesting title",
            "tags": ["interesting", "tag"],
            "category": "news",
            "content": None,
            "draft": False,
            "trusted": False,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    response = await request_create_article(
        client,
        get_test_token,
        {
            "cover": attachment_url,
            "document": [{"text": "Lorem ipsum dor sit amet."}],
            "title": "Article with reused image",
            "tags": ["interesting", "tag"],
            "category": "news",
            "content": None,
            "draft": False,
            "trusted": False,
        },
    )

    # And here goes the errrrrrror!
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "articles:bad_cover"


async def test_articles_cover_bad_author(
    client,
    create_test_user,
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
        get_test_token,
        {
            "cover": attachment_url,
            "document": [{"text": "Lorem ipsum dor sit amet."}],
            "title": "Interesting title",
            "tags": ["interesting", "tag"],
            "category": "news",
            "content": None,
            "draft": False,
            "trusted": False,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "articles:bad_cover"
