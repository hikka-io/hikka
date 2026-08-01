from client_requests import request_create_collection
from client_requests import request_create_article
from client_requests import request_comments_write
from app.sync.feed import generate_feed_session
from client_requests.feed import request_feed
from fastapi import status
from app import constants


async def test_feed(
    client,
    aggregator_anime,
    aggregator_anime_info,
    aggregator_people,
    create_test_user,
    get_test_token,
    test_session,
):
    # Create anime collection
    response = await request_create_collection(
        client,
        get_test_token,
        {
            "visibility": constants.COLLECTION_PUBLIC,
            "description": "Description",
            "title": "Anime collection",
            "content_type": "anime",
            "labels_order": [],
            "tags": ["test"],
            "spoiler": False,
            "nsfw": False,
            "content": [
                {
                    "slug": "fullmetal-alchemist-brotherhood-fc524a",
                    "comment": None,
                    "label": None,
                    "order": 1,
                }
            ],
        },
    )
    assert response.status_code == status.HTTP_200_OK

    # Create article
    response = await request_create_article(
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

    assert response.status_code == status.HTTP_200_OK

    # Create comment on anime
    response = await request_comments_write(
        client,
        get_test_token,
        "anime",
        "fullmetal-alchemist-brotherhood-fc524a",
        "Test comment",
    )

    assert response.status_code == status.HTTP_200_OK

    # Generate feed entries
    await generate_feed_session(test_session)

    # Get feed without filters
    response = await request_feed(client, {}, get_test_token)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3
