from client_requests import request_create_collection
from client_requests import request_create_article
from app.sync.feed import generate_feed_session
from client_requests.feed import request_feed
from fastapi import status
from app import constants


async def test_feed_article_content_types(
    client,
    aggregator_anime,
    aggregator_anime_info,
    aggregator_manga,
    aggregator_manga_info,
    create_test_user,
    get_test_token,
    test_session,
):
    # Create anime article
    await request_create_article(
        client,
        get_test_token,
        {
            "document": [{"text": "Anime article"}],
            "title": "Anime news",
            "category": "news",
            "tags": ["test"],
            "content": {
                "slug": "fullmetal-alchemist-brotherhood-fc524a",
                "content_type": "anime",
            },
            "draft": False,
        },
    )

    # Create manga article
    await request_create_article(
        client,
        get_test_token,
        {
            "document": [{"text": "Manga article"}],
            "title": "Manga news",
            "category": "news",
            "tags": ["test"],
            "content": {
                "slug": "berserk-fb9fbd",
                "content_type": "manga",
            },
            "draft": False,
        },
    )

    # Create collection for good measure
    await request_create_collection(
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

    await generate_feed_session(test_session)

    # Filter articles to anime only, collection should be there as well
    response = await request_feed(
        client,
        {"article_content_types": ["anime"]},
        get_test_token,
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2  # 1 anime article + 1 collection

    # Filter articles to manga only
    response = await request_feed(
        client,
        {"article_content_types": ["manga"]},
        get_test_token,
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2  # 1 manga article + 1 collection
