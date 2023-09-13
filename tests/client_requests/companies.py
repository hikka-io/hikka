def request_companies_search(client, filters={}):
    return client.post("/companies", json=filters)


def request_companies_info(client, slug):
    return client.get(f"/companies/{slug}")


def request_companies_anime(client, slug, company_type=None):
    endpoint = f"/companies/{slug}/anime"

    if company_type:
        endpoint += f"?type={company_type}"

    return client.get(endpoint)
