def request_edit(client, edit_id):
    return client.get(f"/edit/{edit_id}")


def request_create_edit(client, token, content_type, slug, data={}):
    return client.post(
        f"/edit/{content_type}/{slug}",
        headers={"Auth": token},
        json=data,
    )


def request_content_edit_list(client, content_type, slug):
    return client.get(f"/edit/{content_type}/{slug}/list")


def request_approve_edit(client, token, edit_id):
    return client.post(
        f"/edit/{edit_id}/approve",
        headers={"Auth": token},
    )


def request_deny_edit(client, token, edit_id):
    return client.post(
        f"/edit/{edit_id}/deny",
        headers={"Auth": token},
    )
