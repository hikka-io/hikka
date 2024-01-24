def request_companies_search(client, page=1, filters={}):
    return client.post(f"/companies?page={page}", json=filters)


def request_companies_info(client, slug):
    return client.get(f"/companies/{slug}")


def request_companies_anime(client, slug, company_type=None):
    endpoint = f"/companies/{slug}/anime"

    if company_type:
        endpoint += f"?type={company_type}"

    return client.get(endpoint)
