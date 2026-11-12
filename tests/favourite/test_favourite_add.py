from client_requests import request_favourite_add
from client_requests import request_favourite
from app.models import AnimeFavourite, Log
from sqlalchemy import select, desc, func
from fastapi import status
from app import constants
import asyncio


async def test_favourite_add(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
    test_session,
):
    # Add anime to favourite
    response = await request_favourite_add(
        client, "anime", "bocchi-the-rock-9e172d", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK

    # Add anime to favourite one more time to get an error
    response = await request_favourite_add(
        client, "anime", "bocchi-the-rock-9e172d", get_test_token
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "favourite:exists"

    # Check if user has anime in favourite list again
    response = await request_favourite(
        client, "anime", "bocchi-the-rock-9e172d", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK

    # Check anime favourite log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_FAVOURITE
    assert log.user == create_test_user
    assert log.data == {"content_type": "anime"}


async def test_favourite_add_parallel(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
    test_session,
):
    # Same anime added to favourite from several requests at once
    responses = await asyncio.gather(
        *[
            request_favourite_add(
                client, "anime", "bocchi-the-rock-9e172d", get_test_token
            )
            for _ in range(5)
        ]
    )

    # Only one of them should succeed
    status_codes = [response.status_code for response in responses]
    assert status_codes.count(status.HTTP_200_OK) == 1

    for response in responses:
        if response.status_code != status.HTTP_200_OK:
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["code"] == "favourite:exists"

    favourite_count = await test_session.scalar(
        select(func.count(AnimeFavourite.id)).filter(
            AnimeFavourite.user == create_test_user
        )
    )

    assert favourite_count == 1

    favourite_logs_count = await test_session.scalar(
        select(func.count(Log.id)).filter(
            Log.log_type == constants.LOG_FAVOURITE
        )
    )

    assert favourite_logs_count == 1
