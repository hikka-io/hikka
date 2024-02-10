from app.sync.notifications import generate_notifications
from client_requests import request_comments_write
from app.models import Notification
from sqlalchemy import select, func
from app import constants


async def test_notification_tagged_user(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    # Write comment with tagged users
    await request_comments_write(
        client, get_dummy_token, "edit", "17", "@dummy and @testuser"
    )

    # Generate notifications
    await generate_notifications(test_session)

    # Make sure there is only one notification because author can't tag himself
    notifications_count = await test_session.scalar(
        select(func.count(Notification.id)).filter(
            Notification.notification_type == constants.NOTIFICATION_COMMENT_TAG
        )
    )

    assert notifications_count == 1
