from client_requests import request_following
from client_requests import request_followers
from client_requests import request_follow


async def test_follow_status(
    client,
    create_test_user,
    create_dummy_user,
    get_dummy_token,
    get_test_token,
):
    # Follow dummy user by testuser
    response = await request_follow(client, get_test_token, "dummy")

    # Follow testuser user by dummy user
    response = await request_follow(client, get_dummy_token, "testuser")

    # Check following without auth
    response = await request_following(client, "testuser")
    assert response.json()["list"][0]["is_followed"] is False

    # Check following with auth by testuser
    response = await request_following(client, "testuser", get_test_token)
    assert response.json()["list"][0]["is_followed"] is True

    # Check followed without auth
    response = await request_followers(client, "testuser")
    assert response.json()["list"][0]["is_followed"] is False

    # Check followed with auth by testuser
    response = await request_followers(client, "testuser", get_test_token)
    assert response.json()["list"][0]["is_followed"] is True
