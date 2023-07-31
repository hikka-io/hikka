def request_signup(client, email, username, password):
    return client.post(
        "/auth/signup",
        json={"email": email, "username": username, "password": password},
    )


def request_login(client, email, password):
    return client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )


def request_activation(client, token):
    return client.post(
        "/auth/activation",
        json={"token": token},
    )


def request_activation_resend(client, email):
    return client.post(
        "/auth/activation/resend",
        json={"email": email},
    )


def request_password_reset(client, email):
    return client.post(
        "/auth/password/reset",
        json={"email": email},
    )


def request_password_confirm(client, token, new_password):
    return client.post(
        "/auth/password/confirm",
        json={"token": token, "password": new_password},
    )
