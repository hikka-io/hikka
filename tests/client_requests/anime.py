def request_anime_search(client, filters={}, page=1, size=15, token=None):
    headers = {"Auth": token} if token else {}
    return client.post(
        f"/anime?page={page}&size={size}",
        json=filters,
        headers=headers,
    )


def request_anime_genres(client):
    return client.get("/anime/genres")


def request_anime_info(client, slug):
    return client.get(f"/anime/{slug}")


def request_anime_characters(client, slug, page=1):
    return client.get(f"/anime/{slug}/characters?page={page}")


def request_anime_staff(client, slug):
    return client.get(f"/anime/{slug}/staff")


def request_anime_episodes(client, slug, page=1):
    return client.get(f"/anime/{slug}/episodes?page={page}")


def request_anime_recommendations(client, slug, token=None):
    headers = {"Auth": token} if token else {}
    return client.get(f"/anime/{slug}/recommendations", headers=headers)


def request_anime_franchise(client, slug, token=None):
    headers = {"Auth": token} if token else {}
    return client.get(f"/anime/{slug}/franchise", headers=headers)
