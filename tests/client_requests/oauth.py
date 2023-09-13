def request_oauth_url(client, provider):
    return client.get(f"/auth/oauth/{provider}")


def request_oauth_post(client, provider, code=None):
    data = {"code": code} if code else {}

    return client.post(
        f"/auth/oauth/{provider}",
        json=data,
    )
