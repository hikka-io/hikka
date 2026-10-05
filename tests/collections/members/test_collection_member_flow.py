from client_requests import request_collection_member_invite
from client_requests import request_collection_member_accept
from client_requests import request_collection_member_delete
from client_requests import request_collection_members
from client_requests import request_create_collection
from client_requests import request_update_collection
from app.models import CollectionMember, Log
from sqlalchemy import select, desc
from datetime import timedelta
from fastapi import status
from app import constants
import helpers


async def test_collection_member_invite(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    response = await request_create_collection(
        client, get_test_token, helpers.collection_args()
    )

    reference = response.json()["reference"]

    response = await request_collection_member_invite(
        client, reference, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == constants.COLLECTION_MEMBER_PENDING
    assert response.json()["role"] == constants.COLLECTION_MEMBER_EDITOR
    assert response.json()["user"]["username"] == "dummy"
    assert response.json()["invited_by"]["username"] == "testuser"

    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_COLLECTION_MEMBER_INVITE
    assert log.user == create_test_user
    assert log.data["username"] == "dummy"

    # A pending invite grants nothing yet
    response = await request_update_collection(
        client,
        reference,
        get_dummy_token,
        helpers.collection_args(title="Nope now"),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "permission:denied"


async def test_collection_member_invite_errors(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
):
    response = await request_create_collection(
        client, get_test_token, helpers.collection_args()
    )

    reference = response.json()["reference"]

    # Inviting yourself makes no sense
    response = await request_collection_member_invite(
        client, reference, "testuser", get_test_token
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:member_self"

    await request_collection_member_invite(
        client, reference, "dummy", get_test_token
    )

    # Second invite for the same user must be refused
    response = await request_collection_member_invite(
        client, reference, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:member_exists"

    # Co-authors can't hand out access themselves
    response = await request_collection_member_invite(
        client, reference, "testuser", get_dummy_token
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "collections:owner_only"


async def test_collection_member_accept(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
):
    reference = await helpers.create_collection_with_member(
        client, get_test_token
    )

    response = await request_collection_member_accept(
        client, reference, get_dummy_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == constants.COLLECTION_MEMBER_ACCEPTED

    # Accepting twice is not a thing
    response = await request_collection_member_accept(
        client, reference, get_dummy_token
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:member_not_pending"

    # And now editing really works
    response = await request_update_collection(
        client,
        reference,
        get_dummy_token,
        helpers.collection_args(title="Co-edited"),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Co-edited"
    assert response.json()["my_role"] == constants.COLLECTION_MEMBER_EDITOR


async def test_collection_member_accept_without_invite(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
):
    response = await request_create_collection(
        client, get_test_token, helpers.collection_args()
    )

    response = await request_collection_member_accept(
        client, response.json()["reference"], get_dummy_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "collections:member_not_found"


async def test_collection_member_leave(
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

    response = await request_collection_member_delete(
        client, reference, "dummy", get_dummy_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True

    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_COLLECTION_MEMBER_LEAVE

    # Rights are gone immediately, no token invalidation needed
    response = await request_update_collection(
        client,
        reference,
        get_dummy_token,
        helpers.collection_args(title="Left now"),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_collection_member_owner_cant_leave(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
):
    response = await request_create_collection(
        client, get_test_token, helpers.collection_args()
    )

    # The collection must never be left without an owner
    response = await request_collection_member_delete(
        client, response.json()["reference"], "testuser", get_test_token
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:owner_leave"


async def test_collection_member_remove(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_third_user,
    create_dummy_user,
    create_test_user,
    get_third_token,
    get_dummy_token,
    get_test_token,
    test_session,
):
    reference = await helpers.create_collection_with_member(
        client, get_test_token, member_token=get_dummy_token
    )

    # An outsider can't remove anyone
    response = await request_collection_member_delete(
        client, reference, "dummy", get_third_token
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "collections:owner_only"

    response = await request_collection_member_delete(
        client, reference, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK

    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_COLLECTION_MEMBER_REMOVE
    assert log.user == create_test_user
    assert log.data["username"] == "dummy"

    members = (await test_session.scalars(select(CollectionMember))).all()
    assert len(members) == 1
    assert members[0].role == constants.COLLECTION_MEMBER_OWNER


async def test_collection_member_decline(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
):
    reference = await helpers.create_collection_with_member(
        client, get_test_token
    )

    # Declining is removing your own pending row
    response = await request_collection_member_delete(
        client, reference, "dummy", get_dummy_token
    )

    assert response.status_code == status.HTTP_200_OK

    response = await request_collection_member_accept(
        client, reference, get_dummy_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_collection_members_list_hides_pending(
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
        client, get_test_token
    )

    # Owner sees the pending invite
    response = await request_collection_members(
        client, reference, get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2
    assert response.json()["list"][0]["role"] == (
        constants.COLLECTION_MEMBER_OWNER
    )

    # The invited user sees their own pending row
    response = await request_collection_members(
        client, reference, get_dummy_token
    )

    assert response.json()["pagination"]["total"] == 2

    # An outsider sees only accepted members, and the total must agree
    # with the list or it would leak how many invites are out
    response = await request_collection_members(
        client, reference, get_third_token
    )

    assert response.json()["pagination"]["total"] == 1
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["user"]["username"] == "testuser"

    # Same for anonymous requests
    response = await request_collection_members(client, reference)
    assert response.json()["pagination"]["total"] == 1


async def test_collection_member_reinvite_after_decline(
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
        client, get_test_token
    )

    # Declining removes the row outright, there is no declined status
    await request_collection_member_delete(
        client, reference, "dummy", get_dummy_token
    )

    members = (await test_session.scalars(select(CollectionMember))).all()
    assert len(members) == 1
    assert members[0].user_id == create_test_user.id

    # A decline is an explicit no, so the owner can't just ask again
    response = await request_collection_member_invite(
        client, reference, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:member_declined"

    # The cooldown is read from the decline log, so moving that log out of
    # the window is enough to free the owner up again
    log = await test_session.scalar(
        select(Log)
        .filter(Log.log_type == constants.LOG_COLLECTION_MEMBER_DECLINE)
        .order_by(desc(Log.created))
    )

    assert log.data["username"] == "dummy"

    log.created = log.created - timedelta(
        days=constants.COLLECTION_INVITE_COOLDOWN_DAYS + 1
    )
    test_session.add(log)
    await test_session.commit()

    response = await request_collection_member_invite(
        client, reference, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == constants.COLLECTION_MEMBER_PENDING

    # And this time they can accept it
    response = await request_collection_member_accept(
        client, reference, get_dummy_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == constants.COLLECTION_MEMBER_ACCEPTED


async def test_collection_member_reinvite_after_leave(
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

    # Leaving a collection is not the same as refusing to join it
    await request_collection_member_delete(
        client, reference, "dummy", get_dummy_token
    )

    log = await test_session.scalar(
        select(Log).order_by(desc(Log.created))
    )
    assert log.log_type == constants.LOG_COLLECTION_MEMBER_LEAVE

    # So there is no cooldown and the owner may ask them back right away
    response = await request_collection_member_invite(
        client, reference, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == constants.COLLECTION_MEMBER_PENDING


async def test_collection_member_decline_cooldown_per_collection(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
):
    first = (
        await request_create_collection(
            client, get_test_token, helpers.collection_args()
        )
    ).json()["reference"]

    second = (
        await request_create_collection(
            client, get_test_token, helpers.collection_args(title="Another one")
        )
    ).json()["reference"]

    await request_collection_member_invite(
        client, first, "dummy", get_test_token
    )
    await request_collection_member_delete(
        client, first, "dummy", get_dummy_token
    )

    # Declining one collection must not lock the person out of others
    response = await request_collection_member_invite(
        client, second, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK

    # While the collection they refused stays on cooldown
    response = await request_collection_member_invite(
        client, first, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:member_declined"
