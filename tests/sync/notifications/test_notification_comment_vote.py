from app.sync.notifications import generate_notifications
from client_requests import request_comments_write
from client_requests import request_vote
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
    # Write comment for edit
    response = await request_comments_write(
        client, get_dummy_token, "edit", "17", "Nice edit"
    )

    await request_vote(
        client,
        get_test_token,
        constants.CONTENT_COMMENT,
        response.json()["reference"],
        1,
    )

    # Generate notifications
    await generate_notifications(test_session)

    # Make sure there is only one notification
    notifications_count = await test_session.scalar(
        select(
            func.count(Notification.id).filter(
                Notification.notification_type
                == constants.NOTIFICATION_COMMENT_VOTE
            )
        )
    )
    assert notifications_count == 1

    # Get notification
    notificaiton = await test_session.scalar(
        select(Notification).filter(
            Notification.notification_type
            == constants.NOTIFICATION_COMMENT_VOTE
        )
    )

    # And make sure it's correct
    assert notificaiton.user_id == create_dummy_user.id
    assert notificaiton.data["user_score"] == 1
    assert notificaiton.data["new_score"] == 1
    assert notificaiton.data["old_score"] == 0

    # Now change vote to test notification spam prevention
    await request_vote(
        client,
        get_test_token,
        constants.CONTENT_COMMENT,
        response.json()["reference"],
        -1,
    )

    # Generate notifications again
    await generate_notifications(test_session)

    # And make sure there is still only one notification
    notifications_count = await test_session.scalar(
        select(
            func.count(Notification.id).filter(
                Notification.notification_type
                == constants.NOTIFICATION_COMMENT_VOTE
            )
        )
    )
    assert notifications_count == 1
