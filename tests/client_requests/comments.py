def request_comments_write(
    client, token, content_type, slug, text, parent=None
):
    return client.put(
        f"/comments/{content_type}/{slug}",
        headers={"Auth": token},
        json={
            "parent": parent,
            "text": text,
        },
    )


def request_companies_list(client, content_type, slug, page=1):
    return client.get(f"/comments/{content_type}/{slug}/list?page={page}")
