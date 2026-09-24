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


async def test_todo_person_list_search_no_meilisearch(client, aggregator_people):
    # When Meilisearch is down search should throw query down error
    response = await request_todo_person_list(client, {"query": "test"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "search:query_down"


async def test_todo_person_list_search_invalid_query(client, aggregator_people):
    response = await request_todo_person_list(client, {"query": "a"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_todo_person_list_filter_by_invalid_fields(client, aggregator_people):
    response = await request_todo_person_list(client, {"fields": ["bad-field"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_todo_person_list_sort_invalid(client, aggregator_people):
    response = await request_todo_person_list(client, {"sort": ["bad_field:asc"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"

    response = await request_todo_person_list(client, {"sort": ["name_en:bad"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


# These tests scope down to the staff of a single anime (via content_type /
# content_slug) so the field/sort assertions aren't coupled to the full
# ~800-entry people fixture.


async def test_todo_person_list_filter_by_fields(
    client,
    aggregator_anime_roles,
    aggregator_people,
    aggregator_anime,
    aggregator_anime_info,
):
    params = {
        "content_type": "anime",
        "content_slug": "kimi-no-na-wa-945779",
        "size": 50,
    }

    # 7 of the 30 staff members are missing a name_original (name_native)
    response = await request_todo_person_list(
        client, {**params, "fields": ["name_original"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 7

    # Negative entry means "field is present" - the other 23 staff members
    # have a name_original
    response = await request_todo_person_list(
        client, {**params, "fields": ["-name_original"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 23


async def test_todo_person_list_sort_by_name(
    client,
    aggregator_anime_roles,
    aggregator_people,
    aggregator_anime,
    aggregator_anime_info,
):
    response = await request_todo_person_list(
        client,
        {
            "content_type": "anime",
            "content_slug": "kimi-no-na-wa-945779",
            "sort": ["name_en:asc"],
            "size": 50,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"][0]["item"]["name_en"] == "Alexandre Gibert"
    assert response.json()["list"][-1]["item"]["name_en"] == "Yoshitoshi Shinomiya"
