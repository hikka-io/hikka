from client_requests import request_favourite_delete
from client_requests import request_favourite_add
from client_requests import request_favourite
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_favourite_delete(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
    test_session,
):
    # Add anime to favourite
    response = await request_favourite_add(
        client, "bocchi-the-rock-9e172d", get_test_token
    )

    # Bocchi is not our favourite anime anymore...
    response = await request_favourite_delete(
        client, "bocchi-the-rock-9e172d", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True

    # Bocchi is not our favourite anime anymore... again
    response = await request_favourite_delete(
        client, "bocchi-the-rock-9e172d", get_test_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "favourite:not_found"

    # Check whether Bocchi is favourite anime of user one last time
    response = await request_favourite(
        client, "bocchi-the-rock-9e172d", get_test_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "favourite:not_found"

    # Check anime favourite remove log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_FAVOURITE_ANIME_REMOVE
    assert log.user == create_test_user
