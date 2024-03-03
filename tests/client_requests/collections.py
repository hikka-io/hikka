def request_create_collection(client, token, data={}):
    return client.post(
        "/collections/create",
        headers={"Auth": token},
        json=data,
    )


def request_update_collection(client, reference, token, data={}):
    return client.put(
        f"/collections/{reference}",
        headers={"Auth": token},
        json=data,
    )


def request_delete_collection(client, reference, token):
    return client.delete(
        f"/collections/{reference}",
        headers={"Auth": token},
    )


def request_collection_info(client, reference, token=None):
    headers = {"Auth": token} if token else {}
    return client.get(
        f"/collections/{reference}",
        headers=headers,
    )
