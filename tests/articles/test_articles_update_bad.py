from client_requests import request_create_article
from client_requests import request_update_article
from fastapi import status


async def test_articles_update_bad_user(
    client,
    create_test_user,
    create_dummy_user,
    get_test_token,
    get_dummy_token,
    test_session,
):
    response = await request_create_article(
        client,
        get_test_token,
        {
            "cover": None,
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

    response = await request_update_article(
        client,
        article_slug,
        get_dummy_token,
        {
            "cover": None,
            "document": [{"text": "Amet sit dor ipsum lorem."}],
            "title": "Amazing title",
            "tags": ["wow", "tag"],
            "category": "news",
            "content": None,
            "draft": True,
            "trusted": False,
        },
    )

    # Now check error
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"


async def test_articles_update_bad_category(
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

    response = await request_update_article(
        client,
        article_slug,
        get_test_token,
        {
            "cover": None,
            "document": [{"text": "Amet sit dor ipsum lorem."}],
            "title": "Amazing title",
            "tags": ["wow", "tag"],
            "category": "system",
            "content": None,
            "draft": True,
            "trusted": False,
        },
    )

    # Now check error
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "articles:bad_category"


async def test_articles_update_bad_trusted(
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

    response = await request_update_article(
        client,
        article_slug,
        get_test_token,
        {
            "cover": None,
            "document": [{"text": "Amet sit dor ipsum lorem."}],
            "title": "Amazing title",
            "tags": ["wow", "tag"],
            "category": "news",
            "content": None,
            "draft": True,
            "trusted": True,
        },
    )

    # Now check error
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "articles:not_trusted"
