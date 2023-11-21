def request_settings_description(client, token, description):
    return client.put(
        "/settings/description",
        headers={"Auth": token},
        json={"description": description},
    )


def request_settings_username(client, token, username):
    return client.put(
        "/settings/username",
        headers={"Auth": token},
        json={"username": username},
    )
