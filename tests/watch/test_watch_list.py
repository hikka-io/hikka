from client_requests import request_watch_delete
from client_requests import request_watch_list
from client_requests import request_watch_add
from fastapi import status


async def test_watch_add(
    client,
    create_test_user,
    aggregator_anime,
    get_test_token,
):
    # User favourite list should be empty when we start
    response = await request_watch_list(client, "username")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 0

    # Add anime to watch list
    await request_watch_add(
        client,
        "bocchi-the-rock-9e172d",
        get_test_token,
        {
            "status": "watching",
            "episodes": 1,
            "score": 8,
        },
    )

    response = await request_watch_list(client, "username")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["status"] == "watching"
    assert (
        response.json()["list"][0]["anime"]["slug"] == "bocchi-the-rock-9e172d"
    )

    # Add one more anime to watch list
    await request_watch_add(
        client,
        "oshi-no-ko-421060",
        get_test_token,
        {
            "status": "planned",
            "episodes": 0,
            "score": 0,
        },
    )

    response = await request_watch_list(client, "username")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 2
    assert response.json()["list"][0]["status"] == "planned"
    assert response.json()["list"][1]["status"] == "watching"
    assert response.json()["list"][0]["anime"]["slug"] == "oshi-no-ko-421060"
    assert (
        response.json()["list"][1]["anime"]["slug"] == "bocchi-the-rock-9e172d"
    )

    # Try filtering by watch entry staus
    response = await request_watch_list(client, "username", "watching")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["status"] == "watching"
    assert (
        response.json()["list"][0]["anime"]["slug"] == "bocchi-the-rock-9e172d"
    )

    # And now delete Bocchi from user's watch list
    await request_watch_delete(client, "bocchi-the-rock-9e172d", get_test_token)

    response = await request_watch_list(client, "username")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["status"] == "planned"
    assert response.json()["list"][0]["anime"]["slug"] == "oshi-no-ko-421060"
