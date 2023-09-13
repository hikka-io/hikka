from client_requests import request_favourite_list
from client_requests import request_favourite_add
from fastapi import status


async def test_favourite_add(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
):
    # User favourite list should be empty when we start
    response = await request_favourite_list(client, "username")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 0

    # Add anime to favourite
    await request_favourite_add(client, "kimi-no-na-wa-945779", get_test_token)

    # Now let's check again
    response = await request_favourite_list(client, "username")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["anime"]["slug"] == "kimi-no-na-wa-945779"

    # Add one more anime to favourite
    await request_favourite_add(client, "oshi-no-ko-421060", get_test_token)

    # Now let's check again (again)
    response = await request_favourite_list(client, "username")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 2
    assert response.json()["list"][0]["anime"]["slug"] == "oshi-no-ko-421060"
    assert response.json()["list"][1]["anime"]["slug"] == "kimi-no-na-wa-945779"
