from client_requests import request_create_article
from client_requests import request_delete_article
from fastapi import status


async def test_articles_delete_bad(
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
            "document": [
                {
                    "type": "preview",
                    "children": [{"text": "Lorem ipsum dor sit amet."}],
                }
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
        client, article_slug, get_dummy_token
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"
