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


def request_watch_list(client, username, status=None, order=None, sort=None):
    endpoint = f"/watch/{username}/list"
    extra = []

    if status:
        extra.append(f"status={status}")

    if order:
        extra.append(f"order={order}")

    if sort:
        extra.append(f"sort={sort}")

    if len(extra) > 0:
        endpoint += "?" + "&".join(extra)

    return client.get(endpoint)


def request_watch_stats(client, username):
    return client.get(f"/watch/{username}/stats")
