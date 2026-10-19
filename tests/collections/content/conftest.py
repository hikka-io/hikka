from client_requests import request_create_collection
from fastapi import status
from app import constants
import pytest


@pytest.fixture
def create_anime_collection(client):
    async def create(
        token,
        content,
        labels_order=[],
        visibility=constants.COLLECTION_PUBLIC,
        title="Test collection",
    ):
        response = await request_create_collection(
            client,
            token,
            {
                "title": title,
                "tags": [],
                "content_type": "anime",
                "description": "Description",
                "labels_order": labels_order,
                "visibility": visibility,
                "spoiler": False,
                "nsfw": False,
                "content": [
                    {
                        "slug": slug,
                        "comment": None,
                        "label": label,
                        "order": index + 1,
                    }
                    for index, (slug, label) in enumerate(content)
                ],
            },
        )

        assert response.status_code == status.HTTP_200_OK
        return response.json()["reference"]

    return create
