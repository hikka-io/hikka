from app.sync.notifications import generate_notifications
from client_requests import request_comments_write
from client_requests import request_create_edit
from app.models import Notification
from sqlalchemy import select, func
from app import constants


async def test_notification_edit_comment(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
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

    # Write comment for edit
    await request_comments_write(
        client, get_test_token, "edit", "18", "Nice edit"
    )

    # Generate notifications
    await generate_notifications(test_session)

    # Make sure there is only one notification
    notifications_count = await test_session.scalar(
        select(func.count(Notification.id))
    )
    assert notifications_count == 1

    # Get edit comment notification
    notificaiton = await test_session.scalar(select(Notification))

    # And make sure it's correct
    notification_type = constants.NOTIFICATION_EDIT_COMMENT
    assert notificaiton.notification_type == notification_type


async def test_notification_edit_comment_same_author(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
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

    # Write comment for edit
    await request_comments_write(
        client, get_test_token, "edit", "18", "Nice edit"
    )

    # Generate notifications
    await generate_notifications(test_session)

    # Make sure there is only one notification
    notifications_count = await test_session.scalar(
        select(func.count(Notification.id)).filter(
            Notification.notification_type
            == constants.NOTIFICATION_EDIT_COMMENT
        )
    )

    assert notifications_count == 0
