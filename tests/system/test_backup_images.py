from client_requests import request_backup_images
from fastapi import status


async def test_backup_images(client, aggregator_anime):
    response = await request_backup_images(client, "backup_token")
    assert response.status_code == status.HTTP_200_OK

    assert response.json()["pagination"]["total"] == 16
    assert len(response.json()["list"]) == 15

    response = await request_backup_images(client, "bad_token")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
