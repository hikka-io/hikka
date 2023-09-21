def request_watch(client, slug, token):
    return client.get(
        f"/watch/{slug}",
        headers={"Auth": token},
    )


def request_watch_add(client, slug, token, data={}):
    return client.put(
        f"/watch/{slug}",
        headers={"Auth": token},
        json=data,
    )


def request_watch_delete(client, slug, token):
    return client.delete(
        f"/watch/{slug}",
        headers={"Auth": token},
    )


def request_watch_list(client, username, status=None):
    endpoint = f"/watch/{username}/list"

    if status:
        endpoint += f"?status={status}"

    return client.get(endpoint)


def request_watch_stats(client, username):
    return client.get(f"/watch/{username}/stats")
