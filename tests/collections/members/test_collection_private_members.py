from app.sync.collection_invites import expire_collection_invites
from client_requests import request_collection_member_invite
from client_requests import request_collection_member_accept
from client_requests import request_collection_member_delete
from client_requests import request_collection_members
from client_requests import request_create_collection
from client_requests import request_update_collection
from client_requests import request_delete_collection
from client_requests import request_collection_info
from client_requests import request_collections
from app.models import CollectionMember
from sqlalchemy import update
from datetime import timedelta
from app.utils import utcnow
from fastapi import status
from app import constants
import helpers


def collection_args(**kwargs):
    return helpers.collection_args(
        **{"visibility": constants.COLLECTION_PRIVATE, **kwargs}
    )


async def create_private(client, owner_token, **kwargs):
    return await helpers.create_collection_with_member(
        client,
        owner_token,
        visibility=constants.COLLECTION_PRIVATE,
        **kwargs,
    )


async def assert_hidden(client, reference, token=None):
    response = await request_collection_info(client, reference, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "collections:not_found"

    response = await request_collection_members(client, reference, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def profile_references(client, username, token=None):
    response = await request_collections(
        client,
        filters={"author": username, "only_public": False},
        token=token,
    )

    assert response.status_code == status.HTTP_200_OK

    return [collection["reference"] for collection in response.json()["list"]]


async def test_collection_private_invite(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_test_token,
):
    response = await request_create_collection(
        client, get_test_token, collection_args()
    )

    assert response.status_code == status.HTTP_200_OK
    reference = response.json()["reference"]

    response = await request_collection_member_invite(
        client, reference, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == constants.COLLECTION_MEMBER_PENDING


async def test_collection_private_pending_read_only(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
):
    reference = await create_private(client, get_test_token)

    # Pending invitee sees what they are invited to, without a role
    response = await request_collection_info(
        client, reference, get_dummy_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["my_role"] is None

    # Accepted members plus their own pending row
    response = await request_collection_members(
        client, reference, get_dummy_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2
    assert {
        member["user"]["username"]: member["status"]
        for member in response.json()["list"]
    } == {
        "testuser": constants.COLLECTION_MEMBER_ACCEPTED,
        "dummy": constants.COLLECTION_MEMBER_PENDING,
    }

    # Read only means read only
    response = await request_update_collection(
        client, reference, get_dummy_token, collection_args(title="Pending")
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"

    response = await request_delete_collection(
        client, reference, get_dummy_token
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_collection_private_pending_moderator(
    client,
    aggregator_anime,
    aggregator_anime_info,
    moderator_user,
    create_test_user,
    moderator_token,
    get_test_token,
):
    reference = await create_private(
        client, get_test_token, username="moderator"
    )

    # Without the invite a moderator gets 404 here, so a pending invite
    # must not open the moderator path either
    response = await request_update_collection(
        client,
        reference,
        moderator_token,
        collection_args(title="Moderated"),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"

    response = await request_delete_collection(
        client, reference, moderator_token
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"

    response = await request_collection_info(client, reference, get_test_token)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Test collection"


async def test_collection_private_accepted_moderator_cant_delete(
    client,
    aggregator_anime,
    aggregator_anime_info,
    moderator_user,
    create_test_user,
    moderator_token,
    get_test_token,
):
    reference = await create_private(
        client, get_test_token, username="moderator"
    )
    await request_collection_member_accept(client, reference, moderator_token)

    # Editing works as for any co-author, deleting stays with the owner
    response = await request_update_collection(
        client, reference, moderator_token, collection_args(title="Edited")
    )

    assert response.status_code == status.HTTP_200_OK

    response = await request_delete_collection(
        client, reference, moderator_token
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"


async def test_collection_private_accept(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
):
    reference = await create_private(
        client, get_test_token, member_token=get_dummy_token
    )

    response = await request_collection_info(
        client, reference, get_dummy_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["my_role"] == constants.COLLECTION_MEMBER_EDITOR

    response = await request_update_collection(
        client, reference, get_dummy_token, collection_args(title="Edited")
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Edited"


async def test_collection_private_decline(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
):
    reference = await create_private(client, get_test_token)

    response = await request_collection_member_delete(
        client, reference, "dummy", get_dummy_token
    )

    assert response.status_code == status.HTTP_200_OK

    await assert_hidden(client, reference, get_dummy_token)


async def test_collection_private_invite_revoked(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
):
    reference = await create_private(client, get_test_token)

    response = await request_collection_member_delete(
        client, reference, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK

    await assert_hidden(client, reference, get_dummy_token)


async def test_collection_private_leave(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
):
    reference = await create_private(
        client, get_test_token, member_token=get_dummy_token
    )

    response = await request_collection_member_delete(
        client, reference, "dummy", get_dummy_token
    )

    assert response.status_code == status.HTTP_200_OK

    await assert_hidden(client, reference, get_dummy_token)


async def test_collection_private_member_removed(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
):
    reference = await create_private(
        client, get_test_token, member_token=get_dummy_token
    )

    response = await request_collection_member_delete(
        client, reference, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK

    await assert_hidden(client, reference, get_dummy_token)


async def test_collection_private_outsiders(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_third_user,
    create_test_user,
    get_dummy_token,
    get_third_token,
    get_test_token,
):
    reference = await create_private(
        client, get_test_token, member_token=get_dummy_token
    )

    await assert_hidden(client, reference, get_third_token)
    await assert_hidden(client, reference)


async def test_collection_private_from_public_with_members(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_third_user,
    create_test_user,
    get_dummy_token,
    get_third_token,
    get_test_token,
):
    reference = await helpers.create_collection_with_member(
        client, get_test_token, member_token=get_dummy_token
    )

    await request_collection_member_invite(
        client, reference, "thirduser", get_test_token
    )

    # Going private keeps existing members
    response = await request_update_collection(
        client, reference, get_test_token, collection_args()
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["visibility"] == constants.COLLECTION_PRIVATE

    response = await request_collection_members(
        client, reference, get_test_token
    )

    assert response.json()["pagination"]["total"] == 3

    response = await request_collection_info(
        client, reference, get_dummy_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["my_role"] == constants.COLLECTION_MEMBER_EDITOR

    response = await request_collection_info(
        client, reference, get_third_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["my_role"] is None


async def test_collection_private_editor_visibility(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
):
    reference = await create_private(
        client, get_test_token, member_token=get_dummy_token
    )

    response = await request_update_collection(
        client,
        reference,
        get_dummy_token,
        collection_args(visibility=constants.COLLECTION_PUBLIC),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "collections:visibility_owner_only"


async def test_collection_private_profile(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_third_user,
    create_test_user,
    get_dummy_token,
    get_third_token,
    get_test_token,
):
    reference = await create_private(client, get_test_token)

    # Pending invites don't put the collection in the invitee's profile
    assert await profile_references(client, "dummy", get_dummy_token) == []

    await request_collection_member_accept(client, reference, get_dummy_token)

    assert await profile_references(client, "dummy", get_dummy_token) == [
        reference
    ]

    # Private collections never show up in someone else's profile view
    assert await profile_references(client, "dummy", get_third_token) == []
    assert await profile_references(client, "dummy") == []


async def test_collection_private_owner_transfer(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
):
    reference = await create_private(
        client, get_test_token, member_token=get_dummy_token
    )

    await helpers.transfer_ownership(
        client, reference, "dummy", get_test_token, get_dummy_token
    )

    response = await request_collection_info(
        client, reference, get_dummy_token
    )

    assert response.json()["my_role"] == constants.COLLECTION_MEMBER_OWNER

    response = await request_collection_info(client, reference, get_test_token)
    assert response.json()["my_role"] == constants.COLLECTION_MEMBER_EDITOR


async def test_collection_private_invite_expired(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    reference = await create_private(client, get_test_token)

    created = utcnow() - timedelta(
        days=constants.COLLECTION_INVITE_EXPIRE_DAYS + 1
    )

    await test_session.execute(
        update(CollectionMember)
        .filter(CollectionMember.user_id == create_dummy_user.id)
        .values(created=created)
    )
    await test_session.commit()

    await expire_collection_invites(test_session)

    await assert_hidden(client, reference, get_dummy_token)
