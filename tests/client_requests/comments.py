def request_comments_write(
    client, token, content_type, slug, text, parent=None, review=None
):
    return client.put(
        f"/comments/{content_type}/{slug}",
        headers={"Auth": token},
        json={
            "review": review,
            "parent": parent,
            "text": text,
        },
    )


def request_comments_edit(client, token, comment_reference, text, review=None):
    return client.put(
        f"/comments/{comment_reference}",
        headers={"Auth": token},
        json={
            "review": review,
            "text": text,
        },
    )


def request_comments_hide(client, token, comment_reference):
    return client.delete(
        f"/comments/{comment_reference}",
        headers={"Auth": token},
    )


def request_comments_list(client, content_type, slug, token=None, page=1):
    headers = {"Auth": token} if token else {}
    return client.get(
        f"/comments/{content_type}/{slug}/list?page={page}",
        headers=headers,
    )


def request_comments_user(
    client,
    username,
    token=None,
    page=1,
    comment_type="all",
    recommended=None,
    first_level_only=False,
):
    headers = {"Auth": token} if token else {}
    query_string = {
        "first_level_only": str(first_level_only).lower(),
        "comment_type": comment_type,
        "page": page,
    }

    if recommended:
        query_string["recommended"] = recommended

    return client.get(
        f"/comments/user/{username}",
        headers=headers,
        query_string=query_string,
    )


def request_comments_latest(client):
    return client.get("/comments/latest")
