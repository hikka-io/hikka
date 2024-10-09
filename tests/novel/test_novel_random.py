from client_requests import request_novel_random
from fastapi import status


async def test_novel_random(
    client,
    aggregator_genres,
    aggregator_companies,
    aggregator_novel,
    aggregator_novel_info,
):
    # Make request for random novel
    response = await request_novel_random(client)
    assert response.status_code == status.HTTP_200_OK
