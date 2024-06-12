def request_read(client, content_type, slug, token):
    return client.get(
        f"/read/{content_type}/{slug}",
        headers={"Auth": token},
    )


def request_read_add(client, content_type, slug, token, data={}):
    return client.put(
        f"/read/{content_type}/{slug}",
        headers={"Auth": token},
        json=data,
    )


def request_read_delete(client, content_type, slug, token):
    return client.delete(
        f"/read/{content_type}/{slug}",
        headers={"Auth": token},
    )


def request_read_list(
    client, content_type, username, filters={}, page=1, size=15, token=None
):
    headers = {"Auth": token} if token else {}
    return client.post(
        f"/read/{content_type}/{username}/list?page={page}&size={size}",
        json=filters,
        headers=headers,
    )


def request_read_stats(client, content_type, username):
    return client.get(f"/read/{content_type}/{username}/stats")


def request_read_random(client, content_type, username, status):
    return client.get(f"/read/{content_type}/random/{username}/{status}")
