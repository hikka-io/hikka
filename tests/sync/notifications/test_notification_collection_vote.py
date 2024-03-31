from app.sync.notifications import generate_notifications
from client_requests import request_create_collection
from client_requests import request_vote
from app.models import Notification
from sqlalchemy import select, func
from app import constants


async def test_notification_collection_vote(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    # Create test collection
    response = await request_create_collection(
        client,
        get_dummy_token,
        {
            "title": "Test collection",
            "tags": ["romance", "comedy"],
            "content_type": "anime",
            "description": "Description",
            "labels_order": ["Good", "Great"],
            "visibility": constants.COLLECTION_PUBLIC,
            "spoiler": False,
            "nsfw": False,
            "content": [
                {
                    "slug": "fullmetal-alchemist-brotherhood-fc524a",
                    "comment": None,
                    "label": "Good",
                    "order": 1,
                },
                {
                    "slug": "bocchi-the-rock-9e172d",
                    "comment": "Author comment",
                    "label": "Great",
                    "order": 2,
                },
            ],
        },
    )

    await request_vote(
        client,
        get_test_token,
        constants.CONTENT_COLLECTION,
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
                == constants.NOTIFICATION_COLLECTION_VOTE
            )
        )
    )
    assert notifications_count == 1

    # Get notification
    notificaiton = await test_session.scalar(
        select(Notification).filter(
            Notification.notification_type
            == constants.NOTIFICATION_COLLECTION_VOTE
        )
    )

    # And make sure it's correct
    assert notificaiton.user_id == create_dummy_user.id
    assert notificaiton.data["username"] == create_test_user.username
    assert notificaiton.data["user_score"] == 1
    assert notificaiton.data["new_score"] == 1
    assert notificaiton.data["old_score"] == 0
    assert "avatar" in notificaiton.data

    # Now change vote to test notification spam prevention
    await request_vote(
        client,
        get_test_token,
        constants.CONTENT_COLLECTION,
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
                == constants.NOTIFICATION_COLLECTION_VOTE
            )
        )
    )
    assert notifications_count == 1
