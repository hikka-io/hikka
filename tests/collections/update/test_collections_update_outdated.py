from client_requests import request_create_collection
from client_requests import request_update_collection
from app.models import Collection
from sqlalchemy import select
from datetime import timedelta
from fastapi import status
import helpers


async def test_collections_update_outdated(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    response = await request_create_collection(
        client, get_test_token, helpers.collection_args()
    )

    assert response.status_code == status.HTTP_200_OK

    reference = response.json()["reference"]
    stale = response.json()["updated"]

    # Matching timestamp goes through
    response = await request_update_collection(
        client,
        reference,
        get_test_token,
        helpers.collection_args(title="First edit", updated=stale),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "First edit"

    # NOTE: the timestamp is whole seconds, so the edit above has to be
    # moved into the past for this to be a real conflict. That is also the
    # known blind spot of this check: two edits within the same second
    # compare equal and the second one still wins silently
    collection = await test_session.scalar(select(Collection))
    collection.updated = collection.updated + timedelta(minutes=1)
    test_session.add(collection)
    await test_session.commit()

    # The stale timestamp from before that edit must now be rejected,
    # otherwise one co-author would silently overwrite another
    response = await request_update_collection(
        client,
        reference,
        get_test_token,
        helpers.collection_args(title="Second edit", updated=stale),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:outdated"


async def test_collections_update_without_updated(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    response = await request_create_collection(
        client, get_test_token, helpers.collection_args()
    )

    reference = response.json()["reference"]

    # The field is optional, so existing clients keep working unchanged
    response = await request_update_collection(
        client,
        reference,
        get_test_token,
        helpers.collection_args(title="No lock"),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "No lock"
