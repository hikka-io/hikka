from client_requests import request_create_article
from client_requests import request_comments_write
from app.sync.feed import generate_feed_session
from client_requests.feed import request_feed
from fastapi import status


async def test_feed_article_categories(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    # Create news article
    await request_create_article(
        client,
        get_test_token,
        {
            "document": [{"text": "News text"}],
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

    # Create original article
    await request_create_article(
        client,
        get_test_token,
        {
            "document": [{"text": "Original text"}],
            "title": "Original article",
            "category": "original",
            "tags": ["test"],
            "content": {
                "slug": "fullmetal-alchemist-brotherhood-fc524a",
                "content_type": "anime",
            },
            "draft": False,
        },
    )

    # Create comment for a good measure
    await request_comments_write(
        client,
        get_test_token,
        "anime",
        "fullmetal-alchemist-brotherhood-fc524a",
        "Test comment",
    )

    await generate_feed_session(test_session)

    # Filter to news only, comment should be there as well
    response = await request_feed(
        client,
        {"article_categories": ["news"]},
        get_test_token,
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2  # 1 news article + 1 comment

    # Filter to original only
    response = await request_feed(
        client,
        {"article_categories": ["original"]},
        get_test_token,
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2  # 1 original article + 1 comment

    # Filter to reviews — no articles match, comment stays
    response = await request_feed(
        client,
        {"article_categories": ["reviews"]},
        get_test_token,
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1  # only comment
