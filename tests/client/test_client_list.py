from starlette import status

from tests.client_requests import request_list_clients, request_client_create


async def test_client_create(client, test_token, test_user):
    name = "test-client"
    description = "test client description"
    endpoint = "hikka://auth/"
    response = await request_client_create(
        client,
        test_token,
        name,
        description,
        endpoint,
    )
    assert response.status_code == status.HTTP_200_OK

    created_client = response.json()

    response = await request_list_clients(client, test_token)
    assert response.status_code == status.HTTP_200_OK

    json = response.json()

    assert json["pagination"]["total"] == len(json["list"]) == 1

    assert json["list"][0]["reference"] == created_client["reference"]
