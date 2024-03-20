from app.sync.notifications import generate_notifications
from client_requests import request_create_collection
from client_requests import request_comments_write
from app.models import Notification
from sqlalchemy import select, func
from app import constants


async def test_notification_collection_comment(
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

    # Write comment for collection
    await request_comments_write(
        client,
        get_test_token,
        "collection",
        response.json()["reference"],
        "Nice collection",
    )

    # Generate notifications
    await generate_notifications(test_session)

    # Make sure there is only one notification
    notifications_count = await test_session.scalar(
        select(func.count(Notification.id))
    )
    assert notifications_count == 1

    # Get collection comment notification
    notificaiton = await test_session.scalar(select(Notification))

    # And make sure it's correct
    notification_type = constants.NOTIFICATION_COLLECTION_COMMENT
    assert notificaiton.notification_type == notification_type


async def test_notification_collection_comment_same_author(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_test_user,
    get_test_token,
    test_session,
):
    # Create test collection
    response = await request_create_collection(
        client,
        get_test_token,
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

    # Write comment for collection
    await request_comments_write(
        client,
        get_test_token,
        "collection",
        response.json()["reference"],
        "Nice collection",
    )

    # Generate notifications
    await generate_notifications(test_session)

    # Make sure there is only one notification
    notifications_count = await test_session.scalar(
        select(func.count(Notification.id)).filter(
            Notification.notification_type
            == constants.NOTIFICATION_COLLECTION_COMMENT
        )
    )

    assert notifications_count == 0
