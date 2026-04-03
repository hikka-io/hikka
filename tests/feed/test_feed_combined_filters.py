from client_requests import request_create_collection
from client_requests import request_create_article
from client_requests import request_comments_write
from app.sync.feed import generate_feed_session
from client_requests.feed import request_feed
from fastapi import status
from app import constants


async def test_feed_combined_filters(
    client,
    aggregator_anime,
    aggregator_anime_info,
    aggregator_people,
    create_test_user,
    get_test_token,
    test_session,
):
    # Create person collection
    await request_create_collection(
        client,
        get_test_token,
        {
            "visibility": constants.COLLECTION_PUBLIC,
            "title": "People collection",
            "description": "Description",
            "content_type": "person",
            "labels_order": [],
            "tags": ["test"],
            "spoiler": False,
            "nsfw": False,
            "content": [
                {
                    "slug": "justin-cook-77f1b3",
                    "comment": None,
                    "label": None,
                    "order": 1,
                }
            ],
        },
    )

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

    # Create anime comment
    response = await request_comments_write(
        client,
        get_test_token,
        "anime",
        "fullmetal-alchemist-brotherhood-fc524a",
        "Test comment",
    )

    await generate_feed_session(test_session)

    # Filter: anime collections only + reviews articles only + manga comments only
    # Should exclude all
    response = await request_feed(
        client,
        {
            "collection_content_types": ["anime"],
            "article_categories": ["reviews"],
            "comment_content_types": ["manga"],
        },
        get_test_token,
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0

    # Filter: person collections + news articles + anime comments
    # Should include all
    response = await request_feed(
        client,
        {
            "collection_content_types": ["person"],
            "article_categories": ["news"],
            "comment_content_types": ["anime"],
        },
        get_test_token,
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3

    # Filter: person collections + news articles + manga comments
    # Should include some of results
    response = await request_feed(
        client,
        {
            "collection_content_types": ["person"],
            "article_categories": ["news"],
            "comment_content_types": ["manga"],
        },
        get_test_token,
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
