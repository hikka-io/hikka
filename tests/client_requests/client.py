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


def request_client_full_info(client, token: str, client_reference: str):
    return client.get(
        f"/client/{client_reference}/full",
        headers={"Auth": token}
    )

def request_client_info(client, reference: str):
    return client.get(
        f"/client/{reference}"
    )

def request_client_update(
    client,
    token: str,
    client_reference: str,
    name: str | None = None,
    description: str | None = None,
    endpoint: str | None = None,
    revoke_secret: bool = False
):
    return client.put(
        f"/client/{client_reference}",
        headers={"Auth": token},
        json={
            "name": name,
            "description": description,
            "endpoint": endpoint,
            "revoke_secret": revoke_secret
        }
    )


def request_client_delete(
        client, token: str, client_reference: str
):
    return client.delete(
        f"/client/{client_reference}",
        headers={"Auth": token}
    )


def request_list_clients(client, token: str):
    return client.get(
        "/client/",
        headers={"Auth": token},
    )
