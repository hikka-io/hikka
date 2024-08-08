def request_manga_search(client, filters={}, page=1, size=15, token=None):
    headers = {"Auth": token} if token else {}
    return client.post(
        f"/manga?page={page}&size={size}",
        json=filters,
        headers=headers,
    )


def request_manga_info(client, slug):
    return client.get(f"/manga/{slug}")


def request_manga_random(client):
    return client.get("/manga/random")
