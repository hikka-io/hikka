from app.sync.notifications.generate import generate_anime_schedule
from client_requests import request_watch_add
from app.models import Notification, Anime, Log
from sqlalchemy import select, func
from app.utils import utcnow
from app import constants


async def test_notification_anime_schedule(
    client,
    aggregator_anime,
    aggregator_anime_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    slug = "bocchi-the-rock-9e172d"

    await request_watch_add(
        client, slug, get_test_token, {"status": "watching"}
    )
    await request_watch_add(
        client, slug, get_dummy_token, {"status": "planned"}
    )

    anime = await test_session.scalar(select(Anime).filter(Anime.slug == slug))

    log = Log(
        **{
            "log_type": constants.LOG_SCHEDULE_ANIME,
            "target_id": anime.id,
            "created": utcnow(),
            "data": {
                "before": {"episodes_released": 1},
                "after": {"episodes_released": 2},
            },
        }
    )

    test_session.add(log)
    await test_session.commit()

    # Running generator twice must not duplicate notifications
    for _ in range(2):
        await generate_anime_schedule(test_session, log)
        await test_session.commit()

    notifications = (
        await test_session.scalars(
            select(Notification).filter(
                Notification.notification_type
                == constants.NOTIFICATION_SCHEDULE_ANIME
            )
        )
    ).all()

    # Planned entry is skipped when anime status didn't change
    assert [notification.user_id for notification in notifications] == [
        create_test_user.id
    ]

    assert notifications[0].log_id == log.id
    assert notifications[0].data["slug"] == slug

    total = await test_session.scalar(select(func.count(Notification.id)))
    assert total == 1
