from app.sync.notifications import generate_notifications
from client_requests import request_accept_edit
from client_requests import request_create_edit
from app.models import Notification
from sqlalchemy import select, func
from app import constants


async def test_notification_edit_accept(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user_moderator,
    get_dummy_token,
    get_test_token,
    test_session,
):
    # Create edit for anime
    await request_create_edit(
        client,
        get_dummy_token,
        "anime",
        "bocchi-the-rock-9e172d",
        {
            "description": "Brief description",
            "after": {"title_en": "Bocchi The Rock!"},
        },
    )

    # Accept edit
    await request_accept_edit(client, get_test_token, 18)

    # Generate notifications
    await generate_notifications(test_session)

    # Make sure there is only one notification
    notifications_count = await test_session.scalar(
        select(func.count(Notification.id)).filter(
            Notification.notification_type
            == constants.NOTIFICATION_EDIT_ACCEPTED
        )
    )

    assert notifications_count == 1

    notification = await test_session.scalar(
        select(Notification).filter(
            Notification.notification_type
            == constants.NOTIFICATION_EDIT_ACCEPTED
        )
    )

    assert notification.data["username"] == create_test_user_moderator.username
    assert notification.data["edit_id"] == 18
    assert "avatar" in notification.data


async def test_notification_edit_accept_same_author(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user_moderator,
    get_test_token,
    test_session,
):
    # Create edit for anime
    await request_create_edit(
        client,
        get_test_token,
        "anime",
        "bocchi-the-rock-9e172d",
        {
            "description": "Brief description",
            "after": {"title_en": "Bocchi The Rock!"},
        },
    )

    # Accept edit
    await request_accept_edit(client, get_test_token, 18)

    # Generate notifications
    await generate_notifications(test_session)

    # Make sure there is only one notification
    notifications_count = await test_session.scalar(
        select(func.count(Notification.id)).filter(
            Notification.notification_type
            == constants.NOTIFICATION_EDIT_ACCEPTED
        )
    )

    assert notifications_count == 0
