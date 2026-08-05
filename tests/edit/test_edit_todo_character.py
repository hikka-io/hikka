from client_requests import request_todo_character_list
from fastapi import status


async def test_todo_character_list_filter_by_content(
    client,
    aggregator_characters,
    aggregator_anime,
    aggregator_anime_info,
):
    # Levi is one of the characters linked to this anime via aggregator_anime_info
    response = await request_todo_character_list(
        client,
        {
            "content_type": "anime",
            "content_slug": "shingeki-no-kyojin-season-3-part-2-91a350",
            "size": 100,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    slugs = [entry["item"]["slug"] for entry in response.json()["list"]]

    assert "levi-565409" in slugs


async def test_todo_character_list_filter_by_content_no_match(
    client,
    aggregator_characters,
    aggregator_anime,
    aggregator_anime_info,
):
    response = await request_todo_character_list(
        client,
        {"content_type": "anime", "content_slug": "non-existent-slug"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"] == []
    assert response.json()["pagination"]["total"] == 0


async def test_todo_character_list_filter_by_content_wrong_type(
    client,
    aggregator_characters,
    aggregator_anime,
    aggregator_anime_info,
):
    # Levi is linked via anime, not manga, so searching for the same slug
    # under the wrong content type should not match anything
    response = await request_todo_character_list(
        client,
        {
            "content_type": "manga",
            "content_slug": "shingeki-no-kyojin-season-3-part-2-91a350",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"] == []
    assert response.json()["pagination"]["total"] == 0
