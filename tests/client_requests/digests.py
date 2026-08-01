def request_digest(client, username, name, token=None):
    headers = {"Auth": token} if token else None
    return client.get(f"/digests/{username}/{name}", headers=headers)


def request_digest_privacy(client, name, private, token):
    return client.post(
        f"/digests/{name}/privacy",
        json={"private": private},
        headers={"Auth": token},
    )
