from tests.client_requests import request_list_all_clients


async def test_client_list_all(client, admin_token, test_thirdparty_client):
    response = await request_list_all_clients(client, admin_token)
    assert response.status_code == 200

    assert response.json()["pagination"] == {
        "page": 1,
        "pages": 1,
        "total": 1,
    }

    response_client = response.json()["list"][0]
    assert response_client["description"] == test_thirdparty_client.description
    assert response_client["reference"] == test_thirdparty_client.reference
    assert response_client["name"] == test_thirdparty_client.name


async def test_client_list_all_no_permission(client, test_token):
    response = await request_list_all_clients(client, test_token)
    assert response.status_code == 403
