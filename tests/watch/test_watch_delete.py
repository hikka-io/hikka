from client_requests import request_watch_delete
from client_requests import request_watch_add
from client_requests import request_watch
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_watch_delete(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
    test_session,
):
    # Add anime to watch list
    response = await request_watch_add(
        client,
        "bocchi-the-rock-9e172d",
        get_test_token,
        {
            "status": "watching",
            "note": "Test",
            "episodes": 10,
            "score": 8,
        },
    )

    # We did a mistake and now we remove Bocchi from our watch list
    response = await request_watch_delete(
        client, "bocchi-the-rock-9e172d", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True

    # And try to delete it again
    response = await request_watch_delete(
        client, "bocchi-the-rock-9e172d", get_test_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "watch:not_found"

    # Check whether Bocchi is in user's watch list
    response = await request_watch(
        client, "bocchi-the-rock-9e172d", get_test_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "watch:not_found"

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_WATCH_DELETE
    assert log.user == create_test_user
    assert log.data == {}
