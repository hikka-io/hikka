def request_create_article(client, token, data={}):
    return client.post(
        "/articles/create",
        headers={"Auth": token},
        json=data,
    )


def request_update_article(client, slug, token, data={}):
    return client.put(
        f"/articles/{slug}",
        headers={"Auth": token},
        json=data,
    )
