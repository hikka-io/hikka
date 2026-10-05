def request_collections(client, filters={}, page=1, size=15, token=None):
    headers = {"Auth": token} if token else {}
    return client.post(
        f"/collections?page={page}&size={size}",
        json=filters,
        headers=headers,
    )


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


def request_collection_members(
    client, reference, token=None, page=1, size=15
):
    headers = {"Auth": token} if token else {}
    return client.get(
        f"/collections/{reference}/members?page={page}&size={size}",
        headers=headers,
    )


def request_collection_member_invite(client, reference, username, token):
    return client.put(
        f"/collections/{reference}/members/{username}",
        headers={"Auth": token},
    )


def request_collection_member_accept(client, reference, token):
    return client.post(
        f"/collections/{reference}/members/accept",
        headers={"Auth": token},
    )


def request_collection_member_delete(client, reference, username, token):
    return client.delete(
        f"/collections/{reference}/members/{username}",
        headers={"Auth": token},
    )


def request_collection_owner_offer(client, reference, username, token):
    return client.put(
        f"/collections/{reference}/owner/{username}",
        headers={"Auth": token},
    )


def request_collection_owner_accept(client, reference, token):
    return client.post(
        f"/collections/{reference}/owner/accept",
        headers={"Auth": token},
    )


def request_collection_owner_cancel(client, reference, token):
    return client.delete(
        f"/collections/{reference}/owner",
        headers={"Auth": token},
    )
