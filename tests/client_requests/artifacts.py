def request_artifact(client, username, name, token=None):
    headers = {"Auth": token} if token else None
    return client.get(f"/artifacts/{username}/{name}", headers=headers)


def request_artifact_privacy(client, name, private, token):
    return client.post(
        f"/artifacts/{name}/privacy",
        json={"private": private},
        headers={"Auth": token},
    )
