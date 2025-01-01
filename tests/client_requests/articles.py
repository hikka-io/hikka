def request_create_article(client, token, data={}):
    return client.post(
        "/articles/create",
        headers={"Auth": token},
        json=data,
    )


def request_update_article(client, slug, token, data={}):
    return client.put(
        f"/articles/{slug}",
        headers={"Auth": token},
        json=data,
    )


def request_delete_article(client, slug, token):
    return client.delete(
        f"/articles/{slug}",
        headers={"Auth": token},
    )


def request_articles(client, filters={}, page=1, size=15, token=None):
    headers = {"Auth": token} if token else {}
    return client.post(
        f"/articles?page={page}&size={size}",
        json=filters,
        headers=headers,
    )


def request_article_stats(client):
    return client.get("/articles/stats")
