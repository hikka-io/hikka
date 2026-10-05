from client_requests import request_collection_owner_offer
from client_requests import request_comments_write
from client_requests import request_vote
from app.sync.notifications import generate_notifications
from app.models import Notification
from sqlalchemy import select, func
from app import constants
import helpers


async def count_notifications(test_session, notification_type):
    return await test_session.scalar(
        select(
            func.count(Notification.id).filter(
                Notification.notification_type == notification_type
            )
        )
    )


async def test_notification_collection_invite(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_test_token,
    test_session,
):
    reference = await helpers.create_collection_with_member(
        client, get_test_token
    )

    await generate_notifications(test_session)

    notification_type = constants.NOTIFICATION_COLLECTION_INVITE

    assert await count_notifications(test_session, notification_type) == 1

    notification = await test_session.scalar(
        select(Notification).filter(
            Notification.notification_type == notification_type
        )
    )

    # The invite goes to the invited user, from the owner
    assert notification.user_id == create_dummy_user.id
    assert notification.initiator_user_id == create_test_user.id
    assert notification.data["username"] == create_test_user.username
    assert notification.data["slug"] == reference
    assert notification.data["title"] == "Test collection"

    # Running the job again must not duplicate anything
    await generate_notifications(test_session)

    assert await count_notifications(test_session, notification_type) == 1


async def test_notification_collection_owner(
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

    await generate_notifications(test_session)

    notification_type = constants.NOTIFICATION_COLLECTION_OWNER

    assert await count_notifications(test_session, notification_type) == 1

    notification = await test_session.scalar(
        select(Notification).filter(
            Notification.notification_type == notification_type
        )
    )

    assert notification.user_id == create_dummy_user.id
    assert notification.initiator_user_id == create_test_user.id
    assert notification.data["slug"] == reference

    await generate_notifications(test_session)

    assert await count_notifications(test_session, notification_type) == 1


async def test_notification_collection_comment_fanout(
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

    # An outsider comments, so both owner and co-author hear about it
    await request_comments_write(
        client,
        get_third_token,
        constants.CONTENT_COLLECTION,
        reference,
        "Nice collection",
    )

    await generate_notifications(test_session)

    notification_type = constants.NOTIFICATION_COLLECTION_COMMENT

    assert await count_notifications(test_session, notification_type) == 2

    recipients = set(
        await test_session.scalars(
            select(Notification.user_id).filter(
                Notification.notification_type == notification_type
            )
        )
    )

    assert recipients == {create_test_user.id, create_dummy_user.id}

    # Idempotent on a second run
    await generate_notifications(test_session)

    assert await count_notifications(test_session, notification_type) == 2


async def test_notification_collection_comment_skips_author(
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

    # The co-author comments, so only the owner is notified
    await request_comments_write(
        client,
        get_dummy_token,
        constants.CONTENT_COLLECTION,
        reference,
        "Added a few more",
    )

    await generate_notifications(test_session)

    notification_type = constants.NOTIFICATION_COLLECTION_COMMENT

    assert await count_notifications(test_session, notification_type) == 1

    notification = await test_session.scalar(
        select(Notification).filter(
            Notification.notification_type == notification_type
        )
    )

    assert notification.user_id == create_test_user.id


async def test_notification_collection_vote_fanout(
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

    await request_vote(
        client,
        get_third_token,
        constants.CONTENT_COLLECTION,
        reference,
        1,
    )

    await generate_notifications(test_session)

    notification_type = constants.NOTIFICATION_COLLECTION_VOTE

    assert await count_notifications(test_session, notification_type) == 2

    recipients = set(
        await test_session.scalars(
            select(Notification.user_id).filter(
                Notification.notification_type == notification_type
            )
        )
    )

    assert recipients == {create_test_user.id, create_dummy_user.id}
