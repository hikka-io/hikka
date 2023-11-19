def request_edit(client, edit_id):
    return client.get(f"/edit/{edit_id}")


def request_content_edit_list(client, content_type, slug):
    return client.get(f"/edit/{content_type}/{slug}/list")


def request_edit_list(client):
    return client.get("/edit/list")


def request_create_edit(
    client,
    token,
    content_type,
    slug,
    data={},
    captcha="fake_captcha",
):
    return client.put(
        f"/edit/{content_type}/{slug}",
        headers={
            "Auth": token,
            "Captcha": captcha,
        },
        json=data,
    )


def request_update_edit(
    client,
    token,
    edit_id,
    data={},
    captcha="fake_captcha",
):
    return client.post(
        f"/edit/{edit_id}/update",
        headers={
            "Auth": token,
            "Captcha": captcha,
        },
        json=data,
    )


def request_close_edit(client, token, edit_id):
    return client.post(f"/edit/{edit_id}/close", headers={"Auth": token})


def request_accept_edit(client, token, edit_id):
    return client.post(f"/edit/{edit_id}/accept", headers={"Auth": token})


def request_deny_edit(client, token, edit_id):
    return client.post(f"/edit/{edit_id}/deny", headers={"Auth": token})
