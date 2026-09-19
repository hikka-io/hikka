from client_requests import request_create_collection
from sqlalchemy import select
from fastapi import status
from app import constants

from app.models import Collection

from app.sync.search.collections import (
    collections_document_ids_delete,
    collections_documents_total,
    collection_to_document,
    collections_documents,
)


def collection_args(title, visibility=constants.COLLECTION_PUBLIC):
    return {
        "tags": ["тег"],
        "title": title,
        "description": "Description",
        "content_type": "anime",
        "visibility": visibility,
        "labels_order": [],
        "spoiler": False,
        "nsfw": False,
        "content": [
            {
                "order": 1,
                "comment": None,
                "label": None,
                "slug": "bocchi-the-rock-9e172d",
            }
        ],
    }


async def test_search_collections_documents(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    for title, visibility in [
        ("Public collection", constants.COLLECTION_PUBLIC),
        ("Unlisted collection", constants.COLLECTION_UNLISTED),
        ("Private collection", constants.COLLECTION_PRIVATE),
    ]:
        response = await request_create_collection(
            client, get_test_token, collection_args(title, visibility)
        )

        assert response.status_code == status.HTTP_200_OK

    # Only public collections are indexed
    assert await collections_documents_total(test_session) == 1

    documents = await collections_documents(test_session, 1000)

    assert len(documents) == 1
    assert documents[0]["title"] == "Public collection"
    assert documents[0]["content_type"] == "anime"
    assert documents[0]["tags"] == ["тег"]

    # Non public collections are dropped from the index instead
    delete_ids = await collections_document_ids_delete(test_session)
    assert len(delete_ids) == 2

    await test_session.commit()

    # Everything has been processed, so a second pass finds nothing
    assert await collections_documents_total(test_session) == 0
    assert await collections_documents(test_session, 1000) == []
    assert await collections_document_ids_delete(test_session) == []


async def test_search_collections_document_id(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    response = await request_create_collection(
        client, get_test_token, collection_args("Public collection")
    )

    assert response.status_code == status.HTTP_200_OK
    reference = response.json()["reference"]

    collection = await test_session.scalar(select(Collection))
    document = collection_to_document(collection)

    # Collections have no slug, so the document is keyed by reference
    assert document["id"] == reference
