def request_people_search(client, page=1, filters={}):
    return client.post(f"/people?page={page}", json=filters)


def request_people_info(client, slug):
    return client.get(f"/people/{slug}")


def request_people_anime(client, slug):
    return client.get(f"/people/{slug}/anime")
