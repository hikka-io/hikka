from app.sync.notifications import generate_notifications
from client_requests import request_unfollow
from client_requests import request_follow
from app.models import Notification
from sqlalchemy import select, func
from app import constants


async def test_notification_follow(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    # Follow dummy user
    await request_follow(client, get_test_token, "dummy")

    # Generate notifications
    await generate_notifications(test_session)

    # Make sure there is only one notification
    notificaitons_count = await test_session.scalar(
        select(func.count(Notification.id)).filter(
            Notification.notification_type == constants.NOTIFICATION_FOLLOW
        )
    )

    assert notificaitons_count == 1

    # Get follow notification
    notificaiton = await test_session.scalar(
        select(Notification).filter(
            Notification.user_id == create_dummy_user.id
        )
    )

    # And make sure it's correct
    assert notificaiton.notification_type == constants.NOTIFICATION_FOLLOW
    assert notificaiton.data["username"] == create_test_user.username
    assert "avatar" in notificaiton.data

    # Unfollow dummy user and follow again
    await request_unfollow(client, get_test_token, "dummy")
    await request_follow(client, get_test_token, "dummy")

    # Generate notifications again
    await generate_notifications(test_session)

    # And make sure there is still only one notification
    notificaitons_count = await test_session.scalar(
        select(func.count(Notification.id)).filter(
            Notification.notification_type == constants.NOTIFICATION_FOLLOW
        )
    )

    assert notificaitons_count == 1
