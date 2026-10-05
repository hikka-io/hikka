from client_requests import request_collection_owner_accept
from client_requests import request_collection_owner_cancel
from client_requests import request_collection_owner_offer
from client_requests import request_collection_member_invite
from client_requests import request_collection_member_accept
from client_requests import request_collection_member_delete
from client_requests import request_delete_collection
from client_requests import request_create_collection
from client_requests import request_update_collection
from client_requests import request_collection_info
from client_requests import request_collections
from app.collections.service import get_user_collections_count_all
from app.models import CollectionMember, Collection, Log
from sqlalchemy import select, func, desc
from fastapi import status
from app import constants
import helpers


async def test_collection_owner_transfer(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    reference = await helpers.create_collection_with_member(
        client, get_test_token, member_token=get_dummy_token
    )

    response = await request_collection_owner_offer(
        client, reference, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["owner_offered_at"] is not None

    # Nothing has moved yet, the offer still needs an answer
    owner = await test_session.scalar(
        select(CollectionMember).filter(
            CollectionMember.role == constants.COLLECTION_MEMBER_OWNER
        )
    )
    assert owner.user_id == create_test_user.id

    response = await request_collection_owner_accept(
        client, reference, get_dummy_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True

    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_COLLECTION_OWNER_TRANSFER
    assert log.user == create_dummy_user
    assert log.data["username"] == "dummy"

    # Columns rather than entities: the owner row was read above, and an
    # entity query would hand back its stale pre transfer role from the
    # identity map
    members = {
        row.user_id: row.role
        for row in await test_session.execute(
            select(CollectionMember.user_id, CollectionMember.role)
        )
    }

    # Previous owner stays as a co-author and can leave if they want to
    assert members[create_test_user.id] == constants.COLLECTION_MEMBER_EDITOR
    assert members[create_dummy_user.id] == constants.COLLECTION_MEMBER_OWNER

    # There must be exactly one owner at all times
    owners = await test_session.scalar(
        select(func.count(CollectionMember.id)).filter(
            CollectionMember.role == constants.COLLECTION_MEMBER_OWNER
        )
    )
    assert owners == 1

    # author_id is a record of who created the collection and never moves
    collection = await test_session.scalar(select(Collection))
    assert collection.author_id == create_test_user.id


async def test_collection_owner_transfer_moves_rights(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
):
    reference = await helpers.create_collection_with_member(
        client, get_test_token, member_token=get_dummy_token
    )

    await helpers.transfer_ownership(
        client, reference, "dummy", get_test_token, get_dummy_token
    )

    # The new owner can change visibility and delete
    response = await request_update_collection(
        client,
        reference,
        get_dummy_token,
        helpers.collection_args(visibility=constants.COLLECTION_UNLISTED),
    )

    assert response.status_code == status.HTTP_200_OK

    # The previous owner can no longer do either
    response = await request_update_collection(
        client,
        reference,
        get_test_token,
        helpers.collection_args(visibility=constants.COLLECTION_PUBLIC),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "collections:visibility_owner_only"

    response = await request_delete_collection(
        client, reference, get_test_token
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    # But they can still edit content, and they can walk away
    response = await request_update_collection(
        client,
        reference,
        get_test_token,
        helpers.collection_args(
            title="Still editable",
            visibility=constants.COLLECTION_UNLISTED,
        ),
    )

    assert response.status_code == status.HTTP_200_OK

    response = await request_collection_member_delete(
        client, reference, "testuser", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK


async def test_collection_owner_transfer_creator_left(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
):
    reference = await helpers.create_collection_with_member(
        client, get_test_token, member_token=get_dummy_token
    )

    await helpers.transfer_ownership(
        client, reference, "dummy", get_test_token, get_dummy_token
    )
    await request_collection_member_delete(
        client, reference, "testuser", get_test_token
    )

    # A collection the creator left is no longer listed as theirs, even
    # though the response still credits them as the author
    response = await request_collections(
        client, filters={"author": "testuser"}, token=get_test_token
    )

    assert response.json()["pagination"]["total"] == 0

    response = await request_collections(
        client, filters={"author": "dummy"}, token=get_dummy_token
    )

    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["author"]["username"] == "testuser"


async def test_collection_owner_transfer_errors(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_third_user,
    create_dummy_user,
    create_test_user,
    get_third_token,
    get_dummy_token,
    get_test_token,
):
    response = await request_create_collection(
        client, get_test_token, helpers.collection_args()
    )

    reference = response.json()["reference"]

    # Not a member at all
    response = await request_collection_owner_offer(
        client, reference, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "collections:member_not_found"

    await request_collection_member_invite(
        client, reference, "dummy", get_test_token
    )

    # Invited but has not accepted yet, so ownership can't land on them
    response = await request_collection_owner_offer(
        client, reference, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:member_not_accepted"

    await request_collection_member_accept(client, reference, get_dummy_token)

    # Transferring to yourself changes nothing
    response = await request_collection_owner_offer(
        client, reference, "testuser", get_test_token
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:already_owner"

    # Co-authors and outsiders can't transfer the collection
    response = await request_collection_owner_offer(
        client, reference, "dummy", get_dummy_token
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "collections:owner_only"

    response = await request_collection_owner_offer(
        client, reference, "dummy", get_third_token
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_collection_owner_transfer_moves_quota(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    reference = await helpers.create_collection_with_member(
        client, get_test_token, member_token=get_dummy_token
    )

    await helpers.transfer_ownership(
        client, reference, "dummy", get_test_token, get_dummy_token
    )

    # The quota is counted by ownership, so the collection now weighs on
    # the new owner and not on the person who created it. Read through the
    # service directly: the only API path to this count is the 1000
    # collection creation limit, far too heavy to seed here
    assert (
        await get_user_collections_count_all(test_session, create_test_user)
        == 0
    )
    assert (
        await get_user_collections_count_all(test_session, create_dummy_user)
        == 1
    )


async def test_collection_owner_offer_keeps_rights(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
):
    reference = await helpers.create_collection_with_member(
        client, get_test_token, member_token=get_dummy_token
    )

    await request_collection_owner_offer(
        client, reference, "dummy", get_test_token
    )

    # A standing offer must not touch the rights the member already has,
    # which is why it lives in its own column and not in status
    response = await request_update_collection(
        client,
        reference,
        get_dummy_token,
        helpers.collection_args(title="Still an editor"),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["my_role"] == constants.COLLECTION_MEMBER_EDITOR

    # And the owner is still the owner until the offer is answered
    response = await request_collection_info(client, reference, get_test_token)
    assert response.json()["my_role"] == constants.COLLECTION_MEMBER_OWNER


async def test_collection_owner_offer_declined(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    reference = await helpers.create_collection_with_member(
        client, get_test_token, member_token=get_dummy_token
    )

    await request_collection_owner_offer(
        client, reference, "dummy", get_test_token
    )

    response = await request_collection_owner_cancel(
        client, reference, get_dummy_token
    )

    assert response.status_code == status.HTTP_200_OK

    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_COLLECTION_OWNER_CANCEL
    assert log.user == create_dummy_user

    # Nothing moved, and the declined member is still a co-author
    roles = {
        row.user_id: row.role
        for row in await test_session.execute(
            select(CollectionMember.user_id, CollectionMember.role)
        )
    }

    assert roles[create_test_user.id] == constants.COLLECTION_MEMBER_OWNER
    assert roles[create_dummy_user.id] == constants.COLLECTION_MEMBER_EDITOR

    # Nothing left to accept
    response = await request_collection_owner_accept(
        client, reference, get_dummy_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "collections:owner_offer_not_found"


async def test_collection_owner_offer_cancelled_by_owner(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    reference = await helpers.create_collection_with_member(
        client, get_test_token, member_token=get_dummy_token
    )

    await request_collection_owner_offer(
        client, reference, "dummy", get_test_token
    )

    # The owner may change their mind before it is answered
    response = await request_collection_owner_cancel(
        client, reference, get_test_token
    )

    assert response.status_code == status.HTTP_200_OK

    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_COLLECTION_OWNER_CANCEL
    assert log.user == create_test_user


async def test_collection_owner_offer_errors(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_third_user,
    create_dummy_user,
    create_test_user,
    get_third_token,
    get_dummy_token,
    get_test_token,
):
    reference = await helpers.create_collection_with_member(
        client, get_test_token, member_token=get_dummy_token
    )

    # Nothing offered yet
    response = await request_collection_owner_accept(
        client, reference, get_dummy_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "collections:owner_offer_not_found"

    await request_collection_owner_offer(
        client, reference, "dummy", get_test_token
    )

    # Only one offer may stand at a time
    response = await request_collection_owner_offer(
        client, reference, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:owner_offer_exists"

    # An outsider can neither take the collection nor cancel the offer
    response = await request_collection_owner_accept(
        client, reference, get_third_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = await request_collection_owner_cancel(
        client, reference, get_third_token
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "collections:owner_only"
