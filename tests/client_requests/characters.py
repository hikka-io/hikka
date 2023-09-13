def request_characters_search(client, filters={}):
    return client.post("/characters", json=filters)


def request_characters_info(client, slug):
    return client.get(f"/characters/{slug}")


def request_characters_anime(client, slug):
    return client.get(f"/characters/{slug}/anime")
