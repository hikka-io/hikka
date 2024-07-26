def request_client_create(client, token: str, name: str, description: str, endpoint: str):
    return client.post(
        "/client/",
        headers={"Auth": token},
        json={
            "name": name,
            "description": description,
            "endpoint": endpoint,
        }
    )


def request_my_client_info(client, token: str):
    return client.get(
        "/client/",
        headers={"Auth": token}
    )

def request_client_info(client, reference: str):
    return client.get(
        f"/client/{reference}"
    )

def request_client_update(
    client,
    token: str,
    name: str | None = None,
    description: str | None = None,
    endpoint: str | None = None,
    revoke_secret: bool = False
):
    return client.put(
        "/client/",
        headers={"Auth": token},
        json={
            "name": name,
            "description": description,
            "endpoint": endpoint,
            "revoke_secret": revoke_secret
        }
    )


def request_client_delete(
        client, token: str
):
    return client.delete(
        "/client/",
        headers={"Auth": token}
    )
