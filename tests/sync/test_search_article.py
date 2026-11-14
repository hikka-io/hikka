from app.sync.search.article import article_document_ids_delete
from app.sync.search.article import article_documents
from client_requests import request_create_article
from client_requests import request_update_article
from client_requests import request_delete_article
from app.models import Article
from sqlalchemy import select
from fastapi import status


def article_data(title, draft=False, text="Lorem ipsum dor sit amet."):
    return {
        "document": [{"text": text}],
        "title": title,
        "tags": ["search"],
        "category": "news",
        "content": None,
        "draft": draft,
        "trusted": False,
    }


async def get_article(test_session, slug):
    return await test_session.scalar(
        select(Article)
        .filter(Article.slug == slug)
        .execution_options(populate_existing=True)
    )


async def test_search_article_sync(
    client,
    create_test_user,
    get_test_token,
    test_session,
):
    slugs = {}

    for title, draft in [
        ("First article", False),
        ("Draft article", True),
        ("Deleted article", False),
    ]:
        response = await request_create_article(
            client, get_test_token, article_data(title, draft)
        )

        assert response.status_code == status.HTTP_200_OK

        slugs[title] = response.json()["slug"]

    documents, _ = await article_documents(test_session, 1000, None)
    await test_session.commit()

    first = await get_article(test_session, slugs["First article"])
    draft = await get_article(test_session, slugs["Draft article"])
    deleted = await get_article(test_session, slugs["Deleted article"])

    # Documents are keyed on article id and drafts are indexed too
    assert {document["id"] for document in documents} == {
        first.reference,
        draft.reference,
        deleted.reference,
    }

    assert {
        "id": first.reference,
        "title": "First article",
        "slug": first.slug,
    } in documents

    assert first.needs_search_update is False
    assert draft.needs_search_update is False
    assert deleted.needs_search_update is False

    # Title change flags article for search update
    response = await request_update_article(
        client,
        first.slug,
        get_test_token,
        article_data("First article renamed"),
    )

    assert response.status_code == status.HTTP_200_OK

    # Changes that don't touch title or category leave index alone
    response = await request_update_article(
        client,
        draft.slug,
        get_test_token,
        article_data("Draft article", True, "New text"),
    )

    assert response.status_code == status.HTTP_200_OK

    # Deleted article is flagged for removal from index
    response = await request_delete_article(
        client, deleted.slug, get_test_token
    )

    assert response.status_code == status.HTTP_200_OK

    first = await get_article(test_session, slugs["First article"])
    draft = await get_article(test_session, slugs["Draft article"])
    deleted = await get_article(test_session, slugs["Deleted article"])

    assert first.needs_search_update is True
    assert draft.needs_search_update is False
    assert deleted.needs_search_update is True

    documents, _ = await article_documents(test_session, 1000, None)
    delete_ids = await article_document_ids_delete(test_session)
    await test_session.commit()

    assert documents == [
        {
            "id": first.reference,
            "title": "First article renamed",
            "slug": first.slug,
        }
    ]

    assert delete_ids == [deleted.reference]

    first = await get_article(test_session, slugs["First article"])
    deleted = await get_article(test_session, slugs["Deleted article"])

    assert first.needs_search_update is False
    assert deleted.needs_search_update is False
