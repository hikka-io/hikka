def request_create_collection(client, token, data={}):
    return client.post(
        "/collections/create",
        headers={"Auth": token},
        json=data,
    )
