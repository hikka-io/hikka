def request_feed(client, filters={}, token=None):
    headers = {"Auth": token} if token else {}
    return client.post(
        "/feed",
        json=filters,
        headers=headers,
    )
