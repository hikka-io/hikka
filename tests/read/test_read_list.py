from client_requests import request_read_delete
from client_requests import request_read_list
from client_requests import request_read_add
from fastapi import status


async def test_read_list(
    client,
    create_test_user,
    aggregator_manga,
    get_test_token,
):
    # User read list should be empty when we start
    response = await request_read_list(client, "manga", "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 0

    # Add manga to read list
    response = await request_read_add(
        client,
        "manga",
        "berserk-fb9fbd",
        get_test_token,
        {"status": "planned"},
    )

    response = await request_read_list(client, "manga", "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["status"] == "planned"
    assert response.json()["list"][0]["content"]["slug"] == "berserk-fb9fbd"

    # Add one more manga to read list
    response = await request_read_add(
        client,
        "manga",
        "fullmetal-alchemist-7ef8d2",
        get_test_token,
        {
            "status": "reading",
            "note": "Test 2",
            "volumes": 2,
            "chapters": 13,
            "score": 10,
        },
    )

    response = await request_read_list(client, "manga", "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 2
    assert response.json()["list"][0]["status"] == "reading"
    assert response.json()["list"][1]["status"] == "planned"
    assert (
        response.json()["list"][0]["content"]["slug"]
        == "fullmetal-alchemist-7ef8d2"
    )
    assert response.json()["list"][1]["content"]["slug"] == "berserk-fb9fbd"

    # Try filtering by read entry staus
    response = await request_read_list(
        client, "manga", "testuser", {"read_status": "reading"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["status"] == "reading"
    assert (
        response.json()["list"][0]["content"]["slug"]
        == "fullmetal-alchemist-7ef8d2"
    )

    # And now delete Berserk from user's read list
    await request_read_delete(client, "manga", "berserk-fb9fbd", get_test_token)

    response = await request_read_list(client, "manga", "testuser")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["status"] == "reading"
    assert (
        response.json()["list"][0]["content"]["slug"]
        == "fullmetal-alchemist-7ef8d2"
    )
