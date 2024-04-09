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


def request_settings_import_watch(client, token, data):
    return client.post(
        "/settings/import/watch",
        headers={"Auth": token},
        json=data,
    )


def request_settings_delete_image(client, token, image_type):
    return client.delete(
        f"/settings/image/{image_type}", headers={"Auth": token}
    )
