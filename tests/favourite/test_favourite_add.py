from client_requests import request_favourite_add
from client_requests import request_favourite
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_favourite_add(
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

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["anime"]["slug"] == "bocchi-the-rock-9e172d"

    # Add anime to favourite one more time to get an error
    response = await request_favourite_add(
        client, "bocchi-the-rock-9e172d", get_test_token
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "favourite:exists"

    # Check if user has anime in favourite list again
    response = await request_favourite(
        client, "bocchi-the-rock-9e172d", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["anime"]["slug"] == "bocchi-the-rock-9e172d"

    # Check anime favourite log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_FAVOURITE_ANIME
    assert log.user == create_test_user
    assert log.data == {}
