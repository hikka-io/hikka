from client_requests import request_collection_owner_offer
from client_requests import request_collection_member_invite
from client_requests import request_collection_member_accept
from client_requests import request_collection_member_delete
from client_requests import request_collection_members
from client_requests import request_create_collection
from app.models import CollectionMember, AuthToken, Log
from sqlalchemy import select
from app.utils import utcnow
from fastapi import status
from app import constants
import helpers


async def test_collection_member_limit(
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

    reference = response.json()["reference"]

    # Fill the collection up to the limit with pending invites, which
    # count toward the cap so they can't be used to park spam
    for step in range(0, constants.COLLECTION_MEMBERS_LIMIT):
        member_user = await helpers.create_user(
            test_session,
            username=f"member{step}",
            email=f"member{step}@mail.com",
        )

        test_session.add(
            helpers.make_collection_member(
                member_user,
                collection_id=reference,
                status=constants.COLLECTION_MEMBER_PENDING,
                invited_by=create_test_user,
            )
        )

    await helpers.create_user(
        test_session, username="extra", email="extra@mail.com"
    )
    await test_session.commit()

    response = await request_collection_member_invite(
        client, reference, "extra", get_test_token
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:member_limit"


async def test_collection_invites_limit(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_test_token,
    test_session,
):
    response = await request_create_collection(
        client, get_test_token, helpers.collection_args()
    )

    reference = response.json()["reference"]

    # One user's inbox must not be floodable from many collections
    for step in range(0, constants.COLLECTION_INVITES_LIMIT):
        collection = helpers.make_collection(
            create_test_user, title=f"Other collection {step}"
        )

        test_session.add_all(
            [
                collection,
                helpers.make_collection_member(
                    create_dummy_user,
                    collection=collection,
                    status=constants.COLLECTION_MEMBER_PENDING,
                    invited_by=create_test_user,
                ),
            ]
        )

    await test_session.commit()

    response = await request_collection_member_invite(
        client, reference, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:member_invite_limit"


async def test_collection_invites_rate_limit(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_test_token,
    test_session,
):
    response = await request_create_collection(
        client, get_test_token, helpers.collection_args()
    )

    reference = response.json()["reference"]
    now = utcnow()

    for step in range(0, constants.COLLECTION_INVITES_RATE_LIMIT):
        test_session.add(
            Log(
                **{
                    "log_type": constants.LOG_COLLECTION_MEMBER_INVITE,
                    "user": create_test_user,
                    "target_id": reference,
                    "created": now,
                    "data": {},
                }
            )
        )

    await test_session.commit()

    response = await request_collection_member_invite(
        client, reference, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert response.json()["code"] == "system:rate_limit"


async def test_collection_member_banned_invite(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_test_token,
    test_session,
):
    response = await request_create_collection(
        client, get_test_token, helpers.collection_args()
    )

    create_dummy_user.banned = True
    test_session.add(create_dummy_user)
    await test_session.commit()

    response = await request_collection_member_invite(
        client, response.json()["reference"], "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "collections:member_banned"


async def test_collection_member_remove_deleted_user(
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

    create_dummy_user.role = constants.ROLE_DELETED
    test_session.add(create_dummy_user)
    await test_session.commit()

    # A membership row outlives the account, so the owner must still be
    # able to remove it instead of losing a member slot forever
    response = await request_collection_member_delete(
        client, reference, "dummy", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK

    members = (await test_session.scalars(select(CollectionMember))).all()
    assert len(members) == 1
    assert members[0].role == constants.COLLECTION_MEMBER_OWNER


async def test_collection_member_thirdparty_forbidden(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    test_thirdparty_token,
    test_user,
    test_token,
    test_session,
):
    response = await request_create_collection(
        client, test_token, helpers.collection_args()
    )

    reference = response.json()["reference"]

    # Give the client every collection scope there is, so this really
    # tests forbid_thirdparty and not a missing scope
    token = await test_session.scalar(
        select(AuthToken).filter(
            AuthToken.secret == test_thirdparty_token
        )
    )
    token.scope = [constants.SCOPE_COLLECTION]
    test_session.add(token)
    await test_session.commit()

    # An OAuth client must never be able to hand out access to somebody
    # else's collections, no matter what scope it holds
    for response in [
        await request_collection_member_invite(
            client, reference, "dummy", test_thirdparty_token
        ),
        await request_collection_member_accept(
            client, reference, test_thirdparty_token
        ),
        await request_collection_member_delete(
            client, reference, "dummy", test_thirdparty_token
        ),
        await request_collection_owner_offer(
            client, reference, "dummy", test_thirdparty_token
        ),
    ]:
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["code"] == "permission:denied"

    # Reading the member list stays allowed, it is no more revealing
    # than the collection itself
    response = await request_collection_members(
        client, reference, test_thirdparty_token
    )

    assert response.status_code == status.HTTP_200_OK
