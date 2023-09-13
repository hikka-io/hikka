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


def request_following(client, username):
    return client.get(f"/follow/{username}/following")


def request_followers(client, username):
    return client.get(f"/follow/{username}/followers")
