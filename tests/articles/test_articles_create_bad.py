from client_requests import request_create_article
from fastapi import status


async def test_articles_create_bad_category(
    client,
    create_test_user,
    get_test_token,
    test_session,
):
    response = await request_create_article(
        client,
        get_test_token,
        {
            "document": [{"text": "Lorem ipsum dor sit amet."}],
            "title": "Interesting title",
            "tags": ["interesting", "tag"],
            "category": "system",
            "content": None,
            "draft": False,
            "trusted": False,
        },
    )

    # Now check error
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "articles:bad_category"


async def test_articles_create_bad_trusted(
    client,
    create_test_user,
    get_test_token,
    test_session,
):
    response = await request_create_article(
        client,
        get_test_token,
        {
            "document": [{"text": "Lorem ipsum dor sit amet."}],
            "title": "Interesting title",
            "tags": ["interesting", "tag"],
            "category": "news",
            "content": None,
            "draft": False,
            "trusted": True,
        },
    )

    # Now check error
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "articles:not_trusted"
