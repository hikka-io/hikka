def request_related_franchise(client, content_type, slug, token=None):
    headers = {"Auth": token} if token else {}
    return client.get(
        f"/related/{content_type}/{slug}/franchise", headers=headers
    )
