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


def request_watch_list(
    client, username, filters={}, page=1, size=15, token=None
):
    headers = {"Auth": token} if token else {}
    return client.post(
        f"/watch/{username}/list?page={page}&size={size}",
        json=filters,
        headers=headers,
    )


def request_watch_stats(client, username):
    return client.get(f"/watch/{username}/stats")


def request_watch_random(client, username, status):
    return client.get(f"/watch/random/{username}/{status}")
