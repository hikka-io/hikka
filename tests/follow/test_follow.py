from client_requests import request_follow_stats
from client_requests import request_follow_check
from client_requests import request_following
from client_requests import request_followers
from client_requests import request_unfollow
from client_requests import request_follow
from fastapi import status


async def test_not_followed(
    client,
    create_test_user,
    create_dummy_user,
    get_test_token,
):
    # Check if we follow dummy user
    response = await request_follow_check(client, get_test_token, "dummy")
    assert response.json()["follow"] is False
    assert response.status_code == status.HTTP_200_OK


async def test_follow_self(
    client,
    create_test_user,
    get_test_token,
):
    # Make sure user can't follow himself
    response = await request_follow_check(client, get_test_token, "username")
    assert response.json()["code"] == "follow:self"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_follow_unknown_user(
    client,
    create_test_user,
    get_test_token,
):
    # Follow endpoint should throw error if user is not found
    response = await request_follow_check(client, get_test_token, "unknown")
    assert response.json()["code"] == "user:not_found"
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_follow(
    client,
    create_test_user,
    create_dummy_user,
    get_test_token,
):
    # Follow dummy user
    response = await request_follow(client, get_test_token, "dummy")
    assert response.json()["follow"] is True
    assert response.status_code == status.HTTP_200_OK

    # Check if dummy user is being followed
    response = await request_follow_check(client, get_test_token, "dummy")
    assert response.json()["follow"] is True
    assert response.status_code == status.HTTP_200_OK

    # User should not be able to follow same account twice
    response = await request_follow(client, get_test_token, "dummy")
    assert response.json()["code"] == "follow:already_following"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_unfollow(
    client,
    create_test_user,
    create_dummy_user,
    get_test_token,
):
    # Follow dummy user
    response = await request_follow(client, get_test_token, "dummy")
    assert response.json()["follow"] is True
    assert response.status_code == status.HTTP_200_OK

    # Unfollow user
    response = await request_unfollow(client, get_test_token, "dummy")
    assert response.json()["follow"] is False
    assert response.status_code == status.HTTP_200_OK

    # Check if we follow dummy user
    response = await request_follow_check(client, get_test_token, "dummy")
    assert response.json()["follow"] is False
    assert response.status_code == status.HTTP_200_OK

    # User should not be able to unfollow same account twice
    response = await request_unfollow(client, get_test_token, "dummy")
    assert response.json()["code"] == "follow:not_following"
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_stats(
    client,
    create_test_user,
    create_dummy_user,
    get_test_token,
):
    # Follow dummy user
    response = await request_follow(client, get_test_token, "dummy")
    assert response.json()["follow"] is True
    assert response.status_code == status.HTTP_200_OK

    # Check test user stats
    response = await request_follow_stats(client, "username")
    assert response.json() == {"followers": 0, "following": 1}

    # Check dummy user stats
    response = await request_follow_stats(client, "dummy")
    assert response.json() == {"followers": 1, "following": 0}


async def test_followers(
    client,
    create_test_user,
    create_dummy_user,
    get_test_token,
):
    # Follow dummy user
    response = await request_follow(client, get_test_token, "dummy")
    assert response.json()["follow"] is True
    assert response.status_code == status.HTTP_200_OK

    # Check following
    response = await request_following(client, "username")
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["username"] == "dummy"

    # Check followers
    response = await request_followers(client, "dummy")
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["username"] == "username"
