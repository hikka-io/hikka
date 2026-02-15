from client_requests import request_read_add
from client_requests import request_read
from sqlalchemy import select, desc
from app.models import Log
from fastapi import status
from app import constants


async def test_read_add(
    client,
    create_test_user,
    aggregator_manga,
    aggregator_manga_info,
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

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["start_date"] is not None
    assert response.json()["end_date"] is None

    assert response.json()["content"]["slug"] == "berserk-fb9fbd"
    assert response.json()["status"] == "reading"
    assert response.json()["chapters"] == 1
    assert response.json()["volumes"] == 1
    assert response.json()["note"] == "Test"
    assert response.json()["score"] == 8

    start_timestamp = response.json()["start_date"]

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))

    assert log.log_type == constants.LOG_READ_CREATE
    assert log.user == create_test_user

    assert log.data == {
        "after": {
            "note": "Test",
            "score": 8,
            "status": "reading",
            "rereads": 0,
            "volumes": 1,
            "chapters": 1,
            "start_date": response.json()["start_date"],
        },
        "before": {
            "note": None,
            "score": None,
            "status": None,
            "rereads": None,
            "volumes": None,
            "chapters": None,
            "start_date": None,
        },
        "content_type": "manga",
    }

    # Update watch list entry
    response = await request_read_add(
        client,
        "manga",
        "berserk-fb9fbd",
        get_test_token,
        {
            "status": "completed",
            "note": "Test",
            "volumes": 1,
            "chapters": 1,
            "score": 10,
            "start_date": response.json()["start_date"],
            "end_date": response.json()["end_date"],
        },
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["start_date"] is not None
    assert response.json()["end_date"] is not None

    assert response.json()["content"]["slug"] == "berserk-fb9fbd"
    assert response.json()["status"] == "completed"
    assert response.json()["chapters"] == 1
    assert response.json()["volumes"] == 1
    assert response.json()["note"] == "Test"
    assert response.json()["score"] == 10

    # Check user read list
    response = await request_read(
        client, "manga", "berserk-fb9fbd", get_test_token
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["content"]["slug"] == "berserk-fb9fbd"
    assert response.json()["score"] == 10

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))

    assert log.log_type == constants.LOG_READ_UPDATE
    assert log.user == create_test_user
    assert log.data == {
        "after": {
            "score": 10,
            "status": "completed",
            "start_date": response.json()["start_date"],
            "end_date": response.json()["end_date"],
        },
        "before": {
            "score": 8,
            "status": "reading",
            "start_date": start_timestamp,
            "end_date": None,
        },
        "content_type": "manga",
    }

    # Attempt time travel
    response = await request_read_add(
        client,
        "manga",
        "berserk-fb9fbd",
        get_test_token,
        {
            "status": "completed",
            "start_date": response.json()["start_date"],
            "end_date": response.json()["end_date"] - 10000,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
