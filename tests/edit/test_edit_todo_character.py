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


async def test_todo_character_list_search_no_meilisearch(
    client, aggregator_characters
):
    # When Meilisearch is down search should throw query down error
    response = await request_todo_character_list(client, {"query": "test"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "search:query_down"


async def test_todo_character_list_search_invalid_query(
    client, aggregator_characters
):
    response = await request_todo_character_list(client, {"query": "a"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_todo_character_list_filter_by_invalid_fields(
    client, aggregator_characters
):
    response = await request_todo_character_list(client, {"fields": ["bad-field"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_todo_character_list_sort_invalid(client, aggregator_characters):
    response = await request_todo_character_list(client, {"sort": ["bad_field:asc"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"

    response = await request_todo_character_list(client, {"sort": ["name_en:bad"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


# These tests scope down to the cast of a single anime (via content_type /
# content_slug) so the field/sort assertions aren't coupled to the full
# ~400-entry character fixture.


async def test_todo_character_list_filter_by_fields(
    client,
    aggregator_characters,
    aggregator_anime,
    aggregator_anime_info,
):
    params = {
        "content_type": "anime",
        "content_slug": "shingeki-no-kyojin-season-3-part-2-91a350",
        "size": 100,
    }

    # Every character in this cast already has a name_original (name_ja),
    # so filtering for characters missing one should return nothing
    response = await request_todo_character_list(
        client, {**params, "fields": ["name_original"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 0

    # Negative entry means "field is present" - every character in this
    # cast has a name_original, so this must match all of them
    response = await request_todo_character_list(
        client, {**params, "fields": ["-name_original"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 52


async def test_todo_character_list_sort_by_name(
    client,
    aggregator_characters,
    aggregator_anime,
    aggregator_anime_info,
):
    response = await request_todo_character_list(
        client,
        {
            "content_type": "anime",
            "content_slug": "shingeki-no-kyojin-season-3-part-2-91a350",
            "sort": ["name_en:asc"],
            "size": 100,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"][0]["item"]["name_en"] == "Abel"
    assert response.json()["list"][-1]["item"]["name_en"] == "Zeke"
