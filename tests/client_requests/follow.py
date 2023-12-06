def request_follow_check(client, token, username):
    return client.get(
        f"/follow/{username}",
        headers={"Auth": token},
    )


def request_follow(client, token, username):
    return client.put(
        f"/follow/{username}",
        headers={"Auth": token},
    )


def request_unfollow(client, token, username):
    return client.delete(
        f"/follow/{username}",
        headers={"Auth": token},
    )


def request_follow_stats(client, username):
    return client.get(f"/follow/{username}/stats")


def request_following(client, username, token=None):
    headers = {"Auth": token} if token else {}
    return client.get(f"/follow/{username}/following", headers=headers)


def request_followers(client, username, token=None):
    headers = {"Auth": token} if token else {}
    return client.get(f"/follow/{username}/followers", headers=headers)
