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


def request_activation(client, token, captcha="fake_captcha"):
    return client.post(
        "/auth/activation",
        json={"token": token},
        headers={"Captcha": captcha},
    )


def request_activation_resend(client, email, captcha="fake_captcha"):
    return client.post(
        "/auth/activation/resend",
        json={"email": email},
        headers={"Captcha": captcha},
    )


def request_password_reset(client, email, captcha="fake_captcha"):
    return client.post(
        "/auth/password/reset",
        json={"email": email},
        headers={"Captcha": captcha},
    )


def request_password_confirm(
    client, token, new_password, captcha="fake_captcha"
):
    return client.post(
        "/auth/password/confirm",
        json={"token": token, "password": new_password},
        headers={"Captcha": captcha},
    )
