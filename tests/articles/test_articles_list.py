from client_requests import request_create_article
from client_requests import request_article_stats
from client_requests import request_articles
from app.models import Article
from sqlalchemy import select
from fastapi import status
from app import constants
from uuid import uuid4


async def test_articles_list(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user_admin,
    create_dummy_user,
    get_test_token,
    get_dummy_token,
    test_session,
):
    articles = [
        {
            "document": [{"text": "Lorem ipsum dor sit amet."}],
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
            "document": [{"text": "Lorem ipsum dor sit amet. 1"}],
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
            "document": [{"text": "Lorem ipsum dor sit amet. 2"}],
            "title": "Interesting title 2",
            "tags": ["interesting", "meh"],
            "category": "news",
            "content": None,
            "draft": True,
            "trusted": False,
        },
        {
            "document": [{"text": "Lorem ipsum dor sit amet. 3"}],
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
    response = await request_articles(client, filters={"categories": ["news"]})
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
    response = await request_articles(
        client, {"draft": True, "categories": ["news"]}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 0

    # Request drafts while not having any
    response = await request_articles(
        client, {"draft": True, "categories": ["news"]}, token=get_dummy_token
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 0

    # Request drafts
    response = await request_articles(
        client, {"draft": True, "categories": ["news"]}, token=get_test_token
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1

    # Vote score without trusted
    response = await request_articles(
        client,
        {"min_vote_score": 4, "show_trusted": False, "categories": ["news"]},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1

    # Vote score with trusted
    response = await request_articles(
        client,
        {"min_vote_score": 4, "show_trusted": True, "categories": ["news"]},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 3

    # List anime related articles
    response = await request_articles(
        client, {"content_type": "anime", "categories": ["news"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2

    # List articles related to Bocchi
    response = await request_articles(
        client,
        {
            "content_type": "anime",
            "content_slug": "bocchi-the-rock-9e172d",
            "categories": ["news"],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1

    # Check tags top
    response = await request_article_stats(client)
    assert response.status_code == status.HTTP_200_OK
    tags = response.json()["tags"]
    assert len(tags) == 5

    assert tags[0]["name"] == "tag"
    assert tags[0]["content_count"] == 3

    assert tags[1]["name"] == "interesting"
    assert tags[1]["content_count"] == 2

    assert tags[2]["name"] == "blah"
    assert tags[2]["content_count"] == 1

    # When Meilisearch is down search should throw query down error
    response = await request_articles(client, {"query": "test"})

    assert response.json()["code"] == "search:query_down"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_articles_list_search(
    client,
    mock_meilisearch,
    create_test_user,
    get_test_token,
    test_session,
):
    article_ids = {}

    for title, draft in [
        ("Search first", False),
        ("Search second", False),
        ("Search draft", True),
    ]:
        response = await request_create_article(
            client,
            get_test_token,
            {
                "document": [{"text": "Lorem ipsum dor sit amet."}],
                "title": title,
                "tags": ["search"],
                "category": "news",
                "content": None,
                "draft": draft,
                "trusted": False,
            },
        )

        assert response.status_code == status.HTTP_200_OK

        article = await test_session.scalar(
            select(Article).filter(Article.slug == response.json()["slug"])
        )

        article_ids[title] = article.reference

    # Hits include draft which is hidden from general list and
    # stale document of article which doesn't exist
    mock_meilisearch.hits = [
        article_ids["Search first"],
        article_ids["Search draft"],
        str(uuid4()),
    ]

    response = await request_articles(client, {"query": "search"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["title"] == "Search first"

    # Database filters and paginates results so we ask for all hits
    assert mock_meilisearch.calls[0]["page"] == 1
    assert mock_meilisearch.calls[0]["size"] == constants.SEARCH_MAX_HITS

    # Author can search own drafts
    response = await request_articles(
        client, {"query": "search", "draft": True}, token=get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["title"] == "Search draft"

    # Total and pages come from database
    mock_meilisearch.hits = [
        article_ids["Search first"],
        article_ids["Search second"],
    ]

    response = await request_articles(
        client, {"query": "search"}, page=2, size=1
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2
    assert response.json()["pagination"]["pages"] == 2
    assert len(response.json()["list"]) == 1

    # No hits should return empty list instead of all articles
    mock_meilisearch.hits = []

    response = await request_articles(client, {"query": "nothing"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 0
    assert response.json()["list"] == []
