from app.sync.notifications import generate_notifications
from client_requests import request_comments_write
from app.models import Notification
from sqlalchemy import select, func
from app import constants


async def test_notification_edit_comment(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    # Write comment for edit
    await request_comments_write(
        client, get_test_token, "edit", "17", "Nice edit"
    )

    # Generate notifications
    await generate_notifications(test_session)

    # Make sure there is only one notification
    count = await test_session.scalar(select(func.count(Notification.id)))
    assert count == 1

    # Get edit comment notification
    notificaiton = await test_session.scalar(select(Notification))

    # And make sure it's correct
    notification_type = constants.NOTIFICATION_EDIT_COMMENT
    assert notificaiton.notification_type == notification_type
