from client_requests import request_watch
from fastapi import status


async def test_watch(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
):
    # Check whether Bocchi is in user's watch list
    response = await request_watch(
        client, "bocchi-the-rock-9e172d", get_test_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "watch:not_found"
