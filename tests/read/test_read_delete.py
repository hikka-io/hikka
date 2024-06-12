from client_requests import request_read_delete
from client_requests import request_read_add
from client_requests import request_read
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_read_delete(
    client,
    create_test_user,
    aggregator_manga,
    get_test_token,
    test_session,
):
    # Add manga to read list
    response = await request_read_add(
        client,
        "manga",
        "berserk-fb9fbd",
        get_test_token,
        {
            "status": "reading",
            "note": "Test",
            "volumes": 1,
            "chapters": 1,
            "score": 8,
        },
    )

    # We did a mistake and now we remove manga from our read list
    response = await request_read_delete(
        client, "manga", "berserk-fb9fbd", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True

    # And try to delete it again
    response = await request_read_delete(
        client, "manga", "berserk-fb9fbd", get_test_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "read:not_found"

    # Check whether manga is in user's read list
    response = await request_read(
        client, "manga", "berserk-fb9fbd", get_test_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "read:not_found"

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_READ_DELETE
    assert log.user == create_test_user
    assert log.data == {"content_type": "manga"}
