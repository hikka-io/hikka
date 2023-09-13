def request_people_search(client, filters={}):
    return client.post("/people", json=filters)


def request_people_info(client, slug):
    return client.get(f"/people/{slug}")


def request_people_anime(client, slug):
    return client.get(f"/people/{slug}/anime")
