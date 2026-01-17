from sqlalchemy import func, select
from starlette import status

from app import constants
from app.models.system.notification import Notification
from app.sync.notifications import generate_notifications

from tests.client_requests import (
    request_auth_token_request,
    request_client_create,
    request_auth_token,
)


async def test_notification_thirdparty_login(client, test_token, test_session):
    name = "thirdparty-client"
    description = "Third-party client"
    endpoint = "hikka://auth/"
    scope = [constants.SCOPE_READ_USER_DETAILS]

    response = await request_client_create(
        client, test_token, name, description, endpoint
    )
    assert response.status_code == status.HTTP_200_OK

    client_info = response.json()

    client_reference = client_info["reference"]
    client_secret = client_info["secret"]

    response = await request_auth_token_request(
        client,
        test_token,
        client_reference,
        scope,
    )

    assert response.status_code == status.HTTP_200_OK

    request_reference = response.json()["reference"]

    response = await request_auth_token(
        client, request_reference, client_secret
    )
    assert response.status_code == status.HTTP_200_OK

    await generate_notifications(test_session)

    notifications_count = await test_session.scalar(
        select(func.count(Notification.id)).filter(
            Notification.notification_type
            == constants.NOTIFICATION_THIRDPARTY_LOGIN
        )
    )

    assert notifications_count == 1

    notification = await test_session.scalar(
        select(Notification).filter(
            Notification.notification_type
            == constants.NOTIFICATION_THIRDPARTY_LOGIN
        )
    )

    assert notification.data["client"]["name"] == name
    assert notification.data["client"]["description"] == description
    assert notification.data["client"]["reference"] == client_info["reference"]

    assert notification.data["scope"] == scope
