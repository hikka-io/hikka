from client_requests import request_read_stats
from client_requests import request_read_add
from fastapi import status


async def test_read_stats(
    client,
    create_test_user,
    aggregator_manga,
    get_test_token,
):
    # User read stats should be zero when we start
    response = await request_read_stats(client, "manga", "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "completed": 0,
        "reading": 0,
        "planned": 0,
        "on_hold": 0,
        "dropped": 0,
    }

    # Add manga to read list
    response = await request_read_add(
        client,
        "manga",
        "berserk-fb9fbd",
        get_test_token,
        {"status": "planned"},
    )

    # Add one more manga to read list
    response = await request_read_add(
        client,
        "manga",
        "fullmetal-alchemist-7ef8d2",
        get_test_token,
        {"status": "reading"},
    )

    # Now let's check again
    response = await request_read_stats(client, "manga", "testuser")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "completed": 0,
        "reading": 1,
        "planned": 1,
        "on_hold": 0,
        "dropped": 0,
    }
