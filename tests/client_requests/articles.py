def request_create_article(client, token, data={}):
    return client.post(
        "/articles/create",
        headers={"Auth": token},
        json=data,
    )
