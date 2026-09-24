from client_requests import request_todo_novel_list
from fastapi import status


async def test_todo_novel_list(client, aggregator_novel):
    # None of the seeded novels have a synopsis, so all of them show up
    # as having issues by default
    response = await request_todo_novel_list(client)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2
    assert len(response.json()["list"]) == 2


async def test_todo_novel_list_search_no_meilisearch(client, aggregator_novel):
    # When Meilisearch is down search should throw query down error
    response = await request_todo_novel_list(client, {"query": "test"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "search:query_down"


async def test_todo_novel_list_search_invalid_query(client, aggregator_novel):
    response = await request_todo_novel_list(client, {"query": "a"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_todo_novel_list_filter_by_mal_id(client, aggregator_novel):
    response = await request_todo_novel_list(client, {"mal_id": 130826})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["item"]["slug"] == "tian-guan-cifu-7bb159"


async def test_todo_novel_list_filter_by_media_type(client, aggregator_novel):
    response = await request_todo_novel_list(
        client, {"media_type": ["light_novel"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["item"]["mal_id"] == 60553


async def test_todo_novel_list_filter_by_fields(client, aggregator_novel):
    # Every seeded novel already has a title_original, so filtering for
    # novels missing one should return nothing
    response = await request_todo_novel_list(client, {"fields": ["title_original"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 0

    response = await request_todo_novel_list(client, {"fields": ["synopsis_en"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2

    # Negative entry means "field is present" - none of the seeded novels
    # have a synopsis, so this must return nothing
    response = await request_todo_novel_list(client, {"fields": ["-synopsis_en"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 0

    # Every seeded novel has a title_original, so the negative entry
    # (field present) matches all of them
    response = await request_todo_novel_list(client, {"fields": ["-title_original"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2


async def test_todo_novel_list_filter_by_invalid_fields(client, aggregator_novel):
    response = await request_todo_novel_list(client, {"fields": ["bad-field"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_todo_novel_list_filter_by_media_type_list(client, aggregator_novel):
    response = await request_todo_novel_list(
        client, {"media_type": ["novel", "light_novel"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2

    mal_ids = {entry["item"]["mal_id"] for entry in response.json()["list"]}

    assert mal_ids == {130826, 60553}


async def test_todo_novel_list_filter_by_status(client, aggregator_novel):
    response = await request_todo_novel_list(client, {"status": ["finished"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2

    mal_ids = {entry["item"]["mal_id"] for entry in response.json()["list"]}

    assert mal_ids == {130826, 60553}


async def test_todo_novel_list_filter_by_years(client, aggregator_novel):
    response = await request_todo_novel_list(client, {"years": [2020, 2022]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["item"]["mal_id"] == 130826


async def test_todo_novel_list_filter_by_invalid_years(client, aggregator_novel):
    response = await request_todo_novel_list(client, {"years": [2022, 2020]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


# These tests load aggregator_novel_info, which fills in most title/synopsis
# fields. To keep the genre facet filter under test from being coupled to the
# unrelated "any field missing" default fallback, they all pass
# `fields: ["-title_original"]` (title_original/title_ja is present for
# every seeded novel, unlike title_ua which stays missing for both) so the
# full 2-novel set stays in scope.


async def test_todo_novel_list_filter_by_genres(
    client, aggregator_genres, aggregator_novel, aggregator_novel_info
):
    # Both seeded novels have adventure
    response = await request_todo_novel_list(
        client, {"genres": ["adventure"], "fields": ["-title_original"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2

    # Excluding action should filter out tian guan ci fu only
    response = await request_todo_novel_list(
        client, {"genres": ["-action"], "fields": ["-title_original"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["item"]["mal_id"] == 60553


async def test_todo_novel_list_filter_by_magazines(
    client, aggregator_magazines, aggregator_novel, aggregator_novel_info
):
    # None of the seeded novels are linked to a magazine, so this should
    # just confirm the filter is applied without erroring
    response = await request_todo_novel_list(
        client,
        {"magazines": ["young-animal-4f9e5b"], "fields": ["-title_original"]},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 0


async def test_todo_novel_list_sort_by_start_date(client, aggregator_novel):
    response = await request_todo_novel_list(client, {"sort": ["start_date:desc"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"][0]["item"]["mal_id"] == 130826
    assert response.json()["list"][-1]["item"]["mal_id"] == 60553


async def test_todo_novel_list_sort_by_title(client, aggregator_novel):
    response = await request_todo_novel_list(client, {"sort": ["title_en:desc"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"][0]["item"]["mal_id"] == 60553
    assert response.json()["list"][-1]["item"]["mal_id"] == 130826


async def test_todo_novel_list_sort_by_media_type(client, aggregator_novel):
    response = await request_todo_novel_list(client, {"sort": ["media_type:asc"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"][0]["item"]["mal_id"] == 60553
    assert response.json()["list"][-1]["item"]["mal_id"] == 130826

    response = await request_todo_novel_list(client, {"sort": ["media_type:desc"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"][0]["item"]["mal_id"] == 130826
    assert response.json()["list"][-1]["item"]["mal_id"] == 60553


async def test_todo_novel_list_sort_invalid(client, aggregator_novel):
    response = await request_todo_novel_list(client, {"sort": ["bad_field:asc"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"

    response = await request_todo_novel_list(client, {"sort": ["title_en:bad"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"
