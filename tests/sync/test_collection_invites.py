from app.sync.collection_invites import delete_expired_collection_invites
from app.sync.collection_invites import expire_collection_invites
from client_requests import request_create_collection
from app.models import CollectionMember
from sqlalchemy import select, func
from datetime import timedelta
from app.utils import utcnow
from app import constants
import helpers


async def add_member(test_session, reference, user, status_value, age_days):
    created = utcnow() - timedelta(days=age_days)

    test_session.add(
        helpers.make_collection_member(
            user,
            collection_id=reference,
            status=status_value,
            created=created,
        )
    )

    await test_session.commit()


async def test_expire_collection_invites(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_third_user,
    create_dummy_user,
    create_test_user,
    get_test_token,
    test_session,
):
    response = await request_create_collection(
        client, get_test_token, helpers.collection_args()
    )

    reference = response.json()["reference"]
    expire_days = constants.COLLECTION_INVITE_EXPIRE_DAYS

    # Past the deadline, must go
    await add_member(
        test_session,
        reference,
        create_dummy_user,
        constants.COLLECTION_MEMBER_PENDING,
        expire_days + 1,
    )

    # Just inside the deadline, must stay
    await add_member(
        test_session,
        reference,
        create_third_user,
        constants.COLLECTION_MEMBER_PENDING,
        expire_days - 1,
    )

    # An accepted co-author stays no matter how old
    stale_editor = await helpers.create_user(
        test_session, username="stale", email="stale@mail.com"
    )
    await add_member(
        test_session,
        reference,
        stale_editor,
        constants.COLLECTION_MEMBER_ACCEPTED,
        expire_days * 10,
    )

    await expire_collection_invites(test_session)

    remaining = {
        member.user_id: member.status
        for member in (await test_session.scalars(select(CollectionMember)))
    }

    assert create_dummy_user.id not in remaining
    assert (
        remaining[create_third_user.id]
        == constants.COLLECTION_MEMBER_PENDING
    )
    assert (
        remaining[stale_editor.id] == constants.COLLECTION_MEMBER_ACCEPTED
    )
    assert remaining[create_test_user.id] == (
        constants.COLLECTION_MEMBER_ACCEPTED
    )


async def test_expire_collection_invites_commits(
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

    await add_member(
        test_session,
        response.json()["reference"],
        create_dummy_user,
        constants.COLLECTION_MEMBER_PENDING,
        constants.COLLECTION_INVITE_EXPIRE_DAYS + 1,
    )

    # Driven through the scheduler entry point, which opens its own
    # session. sessionmanager.session() does not commit on exit, so
    # without the explicit commit the delete would be rolled back and
    # this job would silently do nothing
    await delete_expired_collection_invites()

    # Read from a different session to prove the delete really landed
    await test_session.commit()

    pending = await test_session.scalar(
        select(func.count(CollectionMember.id)).filter(
            CollectionMember.status == constants.COLLECTION_MEMBER_PENDING
        )
    )

    assert pending == 0


async def test_expire_collection_owner_offer(
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
    stale = utcnow() - timedelta(
        days=constants.COLLECTION_OWNER_OFFER_EXPIRE_DAYS + 1
    )

    await add_member(
        test_session,
        reference,
        create_dummy_user,
        constants.COLLECTION_MEMBER_ACCEPTED,
        0,
    )

    member = await test_session.scalar(
        select(CollectionMember).filter(
            CollectionMember.user_id == create_dummy_user.id
        )
    )
    member.owner_offered_at = stale
    test_session.add(member)
    await test_session.commit()

    await expire_collection_invites(test_session)

    rows = {
        row.user_id: (row.role, row.status, row.owner_offered_at)
        for row in await test_session.execute(
            select(
                CollectionMember.user_id,
                CollectionMember.role,
                CollectionMember.status,
                CollectionMember.owner_offered_at,
            )
        )
    }

    # The offer is withdrawn, but the co-author must still be there:
    # deleting the row would throw them out of the collection instead
    assert len(rows) == 2
    assert rows[create_dummy_user.id] == (
        constants.COLLECTION_MEMBER_EDITOR,
        constants.COLLECTION_MEMBER_ACCEPTED,
        None,
    )
    assert rows[create_test_user.id][0] == constants.COLLECTION_MEMBER_OWNER
