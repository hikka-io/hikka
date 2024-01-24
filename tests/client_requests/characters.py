def request_characters_search(client, page=1, filters={}):
    return client.post(f"/characters?page={page}", json=filters)


def request_characters_info(client, slug):
    return client.get(f"/characters/{slug}")


def request_characters_anime(client, slug):
    return client.get(f"/characters/{slug}/anime")
