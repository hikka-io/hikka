from client_requests import request_edit
from fastapi import status

# ToDo: tests for bad permissions


async def test_edit(client):
    # Try to fetch unknown edit
    response = await request_edit(client, 1)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "edit:not_found"
