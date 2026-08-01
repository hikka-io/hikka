from client_requests import request_create_article
from app.sync.feed import generate_feed_session
from client_requests.feed import request_feed
from client_requests import request_follow
from fastapi import status


async def test_feed_only_followed(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    create_dummy_user,
    get_test_token,
    get_dummy_token,
    test_session,
):
    # Dummy user writes an article
    await request_create_article(
        client,
        get_dummy_token,
        {
            "document": [{"text": "Dummy article"}],
            "title": "Dummy article",
            "category": "news",
            "tags": ["test"],
            "content": {
                "slug": "fullmetal-alchemist-brotherhood-fc524a",
                "content_type": "anime",
            },
            "draft": False,
        },
    )

    # Test user also writes an article
    await request_create_article(
        client,
        get_test_token,
        {
            "document": [{"text": "Test article"}],
            "title": "Test article",
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

    # Without only_followed we should see both
    response = await request_feed(client, {}, get_test_token)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2

    # With only_followed but not following anyone we should see none
    response = await request_feed(
        client, {"only_followed": True}, get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0

    # Follow dummy user
    await request_follow(client, get_test_token, "dummy")

    # Now we should see one article from followed user
    response = await request_feed(
        client, {"only_followed": True}, get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
