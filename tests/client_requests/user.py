def request_me(client, token):
    return client.get(
        "/user/me",
        headers={"Auth": token},
    )


def request_me_ui(client, token):
    return client.get(
        "/user/me/ui",
        headers={"Auth": token},
    )


def request_profile(client, username):
    return client.get(f"/user/{username}")
