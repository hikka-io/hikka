from client_requests import request_create_article
from client_requests import request_article_tags
from client_requests import request_articles
from app.models import Article
from sqlalchemy import select
from fastapi import status


async def test_articles_list(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user_moderator,
    create_dummy_user,
    get_test_token,
    get_dummy_token,
    test_session,
):
    articles = [
        {
            "cover": None,
            "text": "Lorem ipsum dor sit amet.",
            "title": "Interesting title",
            "tags": ["first", "tag"],
            "category": "news",
            "content": {
                "content_type": "anime",
                "slug": "bocchi-the-rock-9e172d",
            },
            "draft": False,
            "trusted": True,
        },
        {
            "cover": None,
            "text": "Lorem ipsum dor sit amet 1.",
            "title": "Interesting title 1",
            "tags": ["interesting", "tag"],
            "category": "news",
            "content": {
                "content_type": "anime",
                "slug": "fullmetal-alchemist-brotherhood-fc524a",
            },
            "draft": False,
            "trusted": True,
        },
        {
            "cover": None,
            "text": "Lorem ipsum dor sit amet 2.",
            "title": "Interesting title 2",
            "tags": ["interesting", "meh"],
            "category": "news",
            "content": None,
            "draft": True,
            "trusted": False,
        },
        {
            "cover": None,
            "text": "Lorem ipsum dor sit amet 3.",
            "title": "Interesting title 3",
            "tags": ["blah", "tag"],
            "category": "news",
            "content": None,
            "draft": False,
            "trusted": False,
        },
    ]

    for article_data in articles:
        response = await request_create_article(
            client, get_test_token, article_data
        )

        # Make sure we got correct response code
        assert response.status_code == status.HTTP_200_OK

    # Test whether drafts are hidden from general list
    response = await request_articles(client, "news")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 3

    article = await test_session.scalar(
        select(Article).filter(
            Article.slug == response.json()["list"][0]["slug"]
        )
    )

    article.vote_score = 5
    test_session.add(article)
    await test_session.commit()

    # Request drafts without auth
    response = await request_articles(client, "news", {"draft": True})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 0

    # Request drafts while not having any
    response = await request_articles(
        client, "news", {"draft": True}, token=get_dummy_token
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 0

    # Request drafts
    response = await request_articles(
        client, "news", {"draft": True}, token=get_test_token
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1

    # Vote score without trusted
    response = await request_articles(
        client,
        "news",
        {"min_vote_score": 4, "show_trusted": False},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1

    # Vote score with trusted
    response = await request_articles(
        client,
        "news",
        {"min_vote_score": 4, "show_trusted": True},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 3

    # List anime related articles
    response = await request_articles(client, "news", {"content_type": "anime"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2

    # List articles related to Bocchi
    response = await request_articles(
        client,
        "news",
        {"content_type": "anime", "content_slug": "bocchi-the-rock-9e172d"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1

    # Check tags top
    response = await request_article_tags(client, "news")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 5

    assert response.json()[0]["name"] == "tag"
    assert response.json()[0]["content_count"] == 3

    assert response.json()[1]["name"] == "interesting"
    assert response.json()[1]["content_count"] == 2

    assert response.json()[2]["name"] == "blah"
    assert response.json()[2]["content_count"] == 1
