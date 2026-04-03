from client_requests import request_create_article
from client_requests import request_comments_write
from app.sync.feed import generate_feed_session
from client_requests.feed import request_feed
from fastapi import status


async def test_feed_comment_content_types(
    client,
    aggregator_anime,
    aggregator_anime_info,
    aggregator_manga,
    aggregator_manga_info,
    create_test_user,
    get_test_token,
    test_session,
):
    # Create anime comment
    await request_comments_write(
        client,
        get_test_token,
        "anime",
        "fullmetal-alchemist-brotherhood-fc524a",
        "Anime comment",
    )

    # Create manga comment
    await request_comments_write(
        client,
        get_test_token,
        "manga",
        "berserk-fb9fbd",
        "Manga comment",
    )

    # Create article just for good measure
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

    # Show only anime comments (artiche should be there)
    response = await request_feed(
        client,
        {"comment_content_types": ["anime"]},
        get_test_token,
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2  # 1 anime comment + 1 article

    # Filter comments to manga only
    response = await request_feed(
        client,
        {"comment_content_types": ["manga"]},
        get_test_token,
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2  # 1 manga comment + 1 article

    # Filter comments to person so there are no comments match, article stays
    response = await request_feed(
        client,
        {"comment_content_types": ["person"]},
        get_test_token,
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1  # only article
