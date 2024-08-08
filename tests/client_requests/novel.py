def request_novel_search(client, filters={}, page=1, size=15, token=None):
    headers = {"Auth": token} if token else {}
    return client.post(
        f"/novel?page={page}&size={size}",
        json=filters,
        headers=headers,
    )


def request_novel_info(client, slug):
    return client.get(f"/novel/{slug}")


def request_novel_random(client):
    return client.get("/novel/random")
