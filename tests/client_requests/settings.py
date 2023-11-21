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


def request_settings_email(client, token, email):
    return client.put(
        "/settings/email",
        headers={"Auth": token},
        json={"email": email},
    )


def request_settings_password(client, token, password):
    return client.put(
        "/settings/password",
        headers={"Auth": token},
        json={"password": password},
    )
