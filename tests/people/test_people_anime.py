from client_requests import request_people_anime
from fastapi import status


async def test_people_anime(
    client,
    aggregator_anime_roles,
    aggregator_people,
    aggregator_anime,
    aggregator_anime_info,
):
    # Get anime Makoto Shinkai worked on
    response = await request_people_anime(client, "makoto-shinkai-943611")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["list"]) == 1

    # Check slugs and roles
    assert response.json()["list"][0]["anime"]["slug"] == "kimi-no-na-wa-945779"
    assert len(response.json()["list"][0]["roles"]) == 7
