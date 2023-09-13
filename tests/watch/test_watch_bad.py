from client_requests import request_watch_add
from fastapi import status


async def test_watch_bad_note(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
):
    # Make sure user can't set note longer than 140 characters
    response = await request_watch_add(
        client,
        "bocchi-the-rock-9e172d",
        get_test_token,
        {
            "note": (
                "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. "
                "Aenean commodo ligula eget dolor. "
                "Aenean massa. Cum sociis natoque penatibus et mag"
            )
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_watch_bad_status(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
):
    # Backend shouldn't let any unexpected statuses trough
    response = await request_watch_add(
        client, "bocchi-the-rock-9e172d", get_test_token, {"status": "bad"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_watch_bad_score(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
):
    # Score should be in range from 0 to 10
    response = await request_watch_add(
        client,
        "bocchi-the-rock-9e172d",
        get_test_token,
        {
            "status": "on_hold",
            "score": -1,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"

    response = await request_watch_add(
        client,
        "bocchi-the-rock-9e172d",
        get_test_token,
        {
            "status": "on_hold",
            "score": 11,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_watch_bad_episodes(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
):
    # Episodes can't be more than what anime has
    response = await request_watch_add(
        client,
        "bocchi-the-rock-9e172d",
        get_test_token,
        {
            "status": "on_hold",
            "episodes": 100,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "watch:bad_episodes"
