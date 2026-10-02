from client_requests import request_update_collection
from client_requests import request_create_collection
from client_requests import request_delete_collection
from client_requests import request_collections
from app.models import Collection
from sqlalchemy import select
from fastapi import status
from app import constants


def collection_args(title="Random anime collection"):
    return {
        "tags": ["тег"],
        "title": title,
        "description": "Description",
        "content_type": "anime",
        "visibility": constants.COLLECTION_PUBLIC,
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


async def test_collections_search_no_meilisearch(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    response = await request_create_collection(
        client, get_test_token, collection_args()
    )

    assert response.status_code == status.HTTP_200_OK

    # When Meilisearch is down search should throw query down error
    response = await request_collections(client, filters={"query": "test"})

    assert response.json()["code"] == "search:query_down"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_collections_search_bad_args(
    client,
    create_test_user,
    get_test_token,
    test_session,
):
    # Query is too short
    response = await request_collections(client, filters={"query": "a"})

    assert response.json()["code"] == "system:validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Tags are validated the same way they are on collection create
    response = await request_collections(client, filters={"tags": ["a"]})

    assert response.json()["code"] == "system:validation_error"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_collections_needs_search_update(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    response = await request_create_collection(
        client, get_test_token, collection_args()
    )

    assert response.status_code == status.HTTP_200_OK
    reference = response.json()["reference"]

    async def get_collection():
        collection = await test_session.scalar(
            select(Collection).filter(Collection.id == reference)
        )

        await test_session.refresh(collection)
        return collection

    # New collections are picked up by the next search update
    collection = await get_collection()
    assert collection.needs_search_update is True

    # Changing the title marks the collection for reindexing
    collection.needs_search_update = False
    test_session.add(collection)
    await test_session.commit()

    response = await request_update_collection(
        client,
        reference,
        get_test_token,
        collection_args(title="Updated anime collection"),
    )

    assert response.status_code == status.HTTP_200_OK

    collection = await get_collection()
    assert collection.needs_search_update is True

    # Deleting the collection marks it for removal from the index
    collection.needs_search_update = False
    test_session.add(collection)
    await test_session.commit()

    response = await request_delete_collection(
        client, reference, get_test_token
    )

    assert response.status_code == status.HTTP_200_OK

    collection = await get_collection()
    assert collection.needs_search_update is True
    assert collection.deleted is True
