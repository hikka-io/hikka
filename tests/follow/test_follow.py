from client_requests import request_follow_stats
from client_requests import request_follow_check
from client_requests import request_following
from client_requests import request_followers
from client_requests import request_unfollow
from client_requests import request_follow
from fastapi import status


# ToDo: Split this test into multiple subtests
async def test_follow(
    client,
    create_test_user,
    create_dummy_user,
    get_test_token,
):
    # Check if we follow dummy user
    response = await request_follow_check(client, get_test_token, "dummy")
    assert response.json()["follow"] is False
    assert response.status_code == status.HTTP_200_OK

    # Follow dummy user
    response = await request_follow(client, get_test_token, "dummy")
    assert response.json()["follow"] is True
    assert response.status_code == status.HTTP_200_OK

    # Check if we follow dummy user again
    response = await request_follow_check(client, get_test_token, "dummy")
    assert response.json()["follow"] is True
    assert response.status_code == status.HTTP_200_OK

    # Check user stats
    response = await request_follow_stats(client, "username")
    assert response.json() == {"followers": 0, "following": 1}

    # Check following
    response = await request_following(client, "username")
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["username"] == "dummy"

    # Check followers
    response = await request_followers(client, "dummy")
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["username"] == "username"

    # Unfollow user
    response = await request_unfollow(client, get_test_token, "dummy")
    assert response.json()["follow"] is False
    assert response.status_code == status.HTTP_200_OK

    # Check if we follow dummy user
    response = await request_follow_check(client, get_test_token, "dummy")
    assert response.json()["follow"] is False
    assert response.status_code == status.HTTP_200_OK
