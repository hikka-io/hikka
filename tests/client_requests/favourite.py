def request_favourite(client, slug, token):
    return client.get(
        f"/favourite/anime/{slug}",
        headers={"Auth": token},
    )


def request_favourite_add(client, slug, token):
    return client.put(
        f"/favourite/anime/{slug}",
        headers={"Auth": token},
    )


def request_favourite_delete(client, slug, token):
    return client.delete(
        f"/favourite/anime/{slug}",
        headers={"Auth": token},
    )


def request_favourite_list(client, username):
    return client.get(f"/favourite/anime/{username}/list")
