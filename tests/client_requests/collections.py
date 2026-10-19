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


def request_user_collections(
    client, token, content_type, content=None, query=None, page=1, size=15
):
    params = {"content_type": content_type, "page": page, "size": size}

    if content:
        params["content"] = content

    if query:
        params["query"] = query

    return client.get(
        "/collections/me",
        query_string=params,
        headers={"Auth": token},
    )


def request_add_collection_content(client, reference, token, slug, data={}):
    return client.put(
        f"/collections/{reference}/content/{slug}",
        headers={"Auth": token},
        json=data,
    )


def request_delete_collection_content(client, reference, token, slug):
    return client.delete(
        f"/collections/{reference}/content/{slug}",
        headers={"Auth": token},
    )
