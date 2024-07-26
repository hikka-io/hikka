from starlette import status

from tests.client_requests import request_client_create, request_client_update


async def test_client_update(client, test_token):
    name = "test-client"
    description = "test client description"
    endpoint = "http://localhost/"

    response = await request_client_create(
        client, test_token, name, description, endpoint
    )
    assert response.status_code == status.HTTP_200_OK

    old_client_info = response.json()
    assert old_client_info["name"] == name
    assert old_client_info["description"] == description
    assert old_client_info["endpoint"] == endpoint

    new_name = "test-client-updated"
    new_description = "test client description updated"
    new_endpoint = "http://localhost/updated"

    response = await request_client_update(
        client,
        test_token,
        new_name,
        new_description,
        new_endpoint,
        revoke_secret=True,
    )
    assert response.status_code == status.HTTP_200_OK

    new_client_info = response.json()
    assert new_client_info["name"] == new_name
    assert new_client_info["description"] == new_description
    assert new_client_info["endpoint"] == new_endpoint

    assert new_client_info["secret"] != old_client_info["secret"]


async def test_client_update_non_existent(client, test_token):
    response = await request_client_update(
        client, test_token, revoke_secret=True
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["code"] == "client:not_found"
