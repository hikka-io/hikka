from client_requests import request_create_article
from app.sync.feed import generate_feed_session
from client_requests.feed import request_feed
from fastapi import status


async def test_feed_no_auth(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    # Test for feed without auth
    await request_create_article(
        client,
        get_test_token,
        {
            "document": [{"text": "Article text"}],
            "title": "News article",
            "category": "news",
            "tags": ["test"],
            "content": {
                "slug": "fullmetal-alchemist-brotherhood-fc524a",
                "content_type": "anime",
            },
            "draft": False,
        },
    )

    await generate_feed_session(test_session)

    # No token
    response = await request_feed(client, {})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
