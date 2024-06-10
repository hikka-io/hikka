from client_requests import request_novel_search
from fastapi import status


async def test_novel_list(
    client,
    aggregator_novel,
    aggregator_novel_info,
):
    # Make request to novel list
    response = await request_novel_search(client)

    from pprint import pprint

    pprint(response.json())

    assert response.status_code == status.HTTP_200_OK

    # Check pagination data
    assert response.json()["pagination"]["total"] == 2
    assert response.json()["pagination"]["pages"] == 1
    assert response.json()["pagination"]["page"] == 1

    # Check first novel slug
    assert response.json()["list"][0]["slug"] == "tian-guan-cifu-7bb159"

    # Check last novel slug
    assert (
        response.json()["list"][1]["slug"]
        == "kono-subarashii-sekai-ni-shukufuku-wo-cc5525"
    )
