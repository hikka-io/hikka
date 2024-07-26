def request_signup(client, email, username, password, captcha="fake_captcha"):
    return client.post(
        "/auth/signup",
        json={
            "email": email,
            "username": username,
            "password": password,
        },
        headers={"Captcha": captcha},
    )


def request_login(client, email, password, captcha="fake_captcha"):
    return client.post(
        "/auth/login",
        json={"email": email, "password": password},
        headers={"Captcha": captcha},
    )


def request_activation(client, token):
    return client.post(
        "/auth/activation",
        json={"token": token},
    )


def request_activation_resend(client, token):
    return client.post(
        "/auth/activation/resend",
        headers={"Auth": token},
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


def request_auth_info(client, token: str):
    return client.get(
        "/auth/info",
        headers={"Auth": token},
    )

def request_auth_token_request(
    client,
    token: str,
    client_reference: str,
    scope: list[str]
):
    return client.post(
        f"/auth/token/request/{client_reference}",
        json={"scope": scope},
        headers={"Auth": token},
    )

def request_auth_token(client, request_reference: str, client_secret: str):
    return client.post(
        "/auth/token",
        json={"request_reference": request_reference, "client_secret": client_secret},


    )
