from client_requests import request_notifications_count
from client_requests import request_notification_seen
from client_requests import request_notifications
from app.models import Notification
from datetime import timedelta
from app.utils import utcnow
from fastapi import status
from app import constants


async def test_notifications_count(
    client,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
    get_test_token,
    test_session,
):
    now = utcnow()
    notifications = [
        Notification(
            **{
                "data": {"step": -1},
                "notification_type": constants.NOTIFICATION_HIKKA_UPDATE,
                "user_id": create_dummy_user.id,
                "created": now,
                "updated": now,
                "log_id": None,
                "seen": False,
            }
        )
    ]

    for step in range(0, 5):
        notifications.append(
            Notification(
                **{
                    "data": {"step": step},
                    "notification_type": constants.NOTIFICATION_HIKKA_UPDATE,
                    "created": now + timedelta(minutes=step),
                    "updated": now + timedelta(minutes=step),
                    "user_id": create_test_user.id,
                    "log_id": None,
                    "seen": False,
                }
            )
        )

    test_session.add_all(notifications)
    await test_session.commit()

    # Get user notifications
    response = await request_notifications(client, get_test_token)

    # Check status and notifications
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 5

    notification_reference = response.json()["list"][1]["reference"]

    # Now let's get notifications count
    response = await request_notifications_count(client, get_test_token)

    # Check status and notifications count
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["unseen"] == 5

    # Now mark notification as seen
    response = await request_notification_seen(
        client, notification_reference, get_test_token
    )

    assert response.status_code == status.HTTP_200_OK

    # Now let's check whether notifications has been marked as read correctly
    response = await request_notifications(client, get_test_token)

    assert response.json()["list"][0]["seen"] is False
    assert response.json()["list"][1]["seen"] is True
    assert response.json()["list"][2]["seen"] is True
    assert response.json()["list"][3]["seen"] is True
    assert response.json()["list"][4]["seen"] is True

    # And check unseen count
    response = await request_notifications_count(client, get_test_token)
    assert response.json()["unseen"] == 1

    # Check dummy user notifications count just in case
    # We used to had a bug which marked all notification of seen
    response = await request_notifications_count(client, get_dummy_token)
    assert response.json()["unseen"] == 1


async def test_notification_initiator(
    client, create_dummy_user, test_user, test_session, test_token
):
    now = utcnow()
    test_session.add(
        Notification(
            **{
                "notification_type": constants.NOTIFICATION_HIKKA_UPDATE,
                "data": {},
                "log_id": None,
                "seen": False,
                "user": test_user,
                "initiator_user": create_dummy_user,
                "created": now,
                "updated": now,
            }
        )
    )
    await test_session.commit()

    response = await request_notifications(client, test_token)
    print(response.json())
    assert response.status_code == status.HTTP_200_OK

    initiator_user = response.json()["list"][0]["initiator_user"]

    assert initiator_user["reference"] == create_dummy_user.reference
    assert initiator_user["username"] == create_dummy_user.username
    assert initiator_user["role"] == create_dummy_user.role
    assert initiator_user["avatar"] == create_dummy_user.avatar
    assert initiator_user["cover"] == create_dummy_user.cover
