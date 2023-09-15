def request_edit(client, edit_id):
    return client.get(f"/edit/{edit_id}")


def request_create_edit(client, token, content_type, slug, data={}):
    return client.post(
        f"/edit/{content_type}/{slug}",
        headers={"Auth": token},
        json=data,
    )
