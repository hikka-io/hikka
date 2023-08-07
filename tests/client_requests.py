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


def request_oauth_url(client, provider):
    return client.get(f"/auth/oauth/{provider}")


def oauth_post(client, provider, code=None):
    data = {"code": code} if code else {}

    return client.post(
        f"/auth/oauth/{provider}",
        json=data,
    )


def request_me(client, token):
    return client.get("/user/me", headers={"Auth": token})


def request_profile(client, username):
    return client.get(f"/user/{username}")
