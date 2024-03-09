from client_requests import request_favourite
from fastapi import status


async def test_favourite(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
):
    # Check whether Bocchi is favourite anime of user
    response = await request_favourite(
        client, "anime", "bocchi-the-rock-9e172d", get_test_token
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "favourite:not_found"
