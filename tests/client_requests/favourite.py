def request_favourite(client, content_type, slug, token):
    return client.get(
        f"/favourite/{content_type}/{slug}",
        headers={"Auth": token},
    )


def request_favourite_add(client, content_type, slug, token):
    return client.put(
        f"/favourite/{content_type}/{slug}",
        headers={"Auth": token},
    )


def request_favourite_delete(client, content_type, slug, token):
    return client.delete(
        f"/favourite/{content_type}/{slug}",
        headers={"Auth": token},
    )


def request_favourite_list(client, content_type, username, token=None):
    headers = {"Auth": token} if token else {}

    return client.post(
        f"/favourite/{content_type}/{username}/list",
        headers=headers,
    )
