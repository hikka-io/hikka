def request_edit(client, edit_id):
    return client.get(f"/edit/{edit_id}")


def request_todo_anime_list(client, params={}):
    params = dict(params)
    query = {}

    for key in ("page", "size"):
        if key in params:
            query[key] = params.pop(key)

    return client.post("/edit/todo/anime", query_string=query, json=params)


def request_todo_manga_list(client, params={}):
    params = dict(params)
    query = {}

    for key in ("page", "size"):
        if key in params:
            query[key] = params.pop(key)

    return client.post("/edit/todo/manga", query_string=query, json=params)


def request_todo_novel_list(client, params={}):
    params = dict(params)
    query = {}

    for key in ("page", "size"):
        if key in params:
            query[key] = params.pop(key)

    return client.post("/edit/todo/novel", query_string=query, json=params)


def request_todo_character_list(client, params={}):
    params = dict(params)
    query = {}

    for key in ("page", "size"):
        if key in params:
            query[key] = params.pop(key)

    return client.post("/edit/todo/characters", query_string=query, json=params)


def request_todo_person_list(client, params={}):
    params = dict(params)
    query = {}

    for key in ("page", "size"):
        if key in params:
            query[key] = params.pop(key)

    return client.post("/edit/todo/people", query_string=query, json=params)


def request_edit_list(client, filters={}, page=1, size=15, token=None):
    headers = {"Auth": token} if token else {}
    return client.post(
        f"/edit/list?page={page}&size={size}",
        json=filters,
        headers=headers,
    )


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
