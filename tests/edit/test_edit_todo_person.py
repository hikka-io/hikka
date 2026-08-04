from client_requests import request_todo_person_list
from fastapi import status


async def test_todo_person_list_filter_by_content(
    client,
    aggregator_anime_roles,
    aggregator_people,
    aggregator_anime,
    aggregator_anime_info,
):
    # Makoto Shinkai worked on this anime via aggregator_anime_info, among
    # 30 other staff members, so raise the page size to make sure he's
    # included in the response
    response = await request_todo_person_list(
        client,
        {
            "content_type": "anime",
            "content_slug": "kimi-no-na-wa-945779",
            "size": 50,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    slugs = [entry["item"]["slug"] for entry in response.json()["list"]]

    assert "makoto-shinkai-943611" in slugs


async def test_todo_person_list_filter_by_content_no_match(
    client,
    aggregator_anime_roles,
    aggregator_people,
    aggregator_anime,
    aggregator_anime_info,
):
    response = await request_todo_person_list(
        client,
        {"content_type": "anime", "content_slug": "non-existent-slug"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"] == []
    assert response.json()["pagination"]["total"] == 0


async def test_todo_person_list_filter_by_content_wrong_type(
    client,
    aggregator_anime_roles,
    aggregator_people,
    aggregator_anime,
    aggregator_anime_info,
):
    # Makoto Shinkai is linked via anime, not novel, so searching for the
    # same slug under the wrong content type should not match anything
    response = await request_todo_person_list(
        client,
        {"content_type": "novel", "content_slug": "kimi-no-na-wa-945779"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"] == []
    assert response.json()["pagination"]["total"] == 0
