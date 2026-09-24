from client_requests import request_todo_manga_list
from fastapi import status


async def test_todo_manga_list(client, aggregator_manga):
    # None of the seeded manga have a synopsis, so all of them show up
    # as having issues by default
    response = await request_todo_manga_list(client)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 4
    assert len(response.json()["list"]) == 4


async def test_todo_manga_list_search_no_meilisearch(client, aggregator_manga):
    # When Meilisearch is down search should throw query down error
    response = await request_todo_manga_list(client, {"query": "test"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "search:query_down"


async def test_todo_manga_list_search_invalid_query(client, aggregator_manga):
    response = await request_todo_manga_list(client, {"query": "a"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_todo_manga_list_filter_by_mal_id(client, aggregator_manga):
    response = await request_todo_manga_list(client, {"mal_id": 2})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["item"]["slug"] == "berserk-fb9fbd"


async def test_todo_manga_list_filter_by_media_type(client, aggregator_manga):
    response = await request_todo_manga_list(client, {"media_type": ["manhwa"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["item"]["mal_id"] == 125036


async def test_todo_manga_list_filter_by_fields(client, aggregator_manga):
    # Every seeded manga already has a title_original, so filtering for
    # manga missing one should return nothing
    response = await request_todo_manga_list(client, {"fields": ["title_original"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 0

    response = await request_todo_manga_list(client, {"fields": ["synopsis_en"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 4

    # Negative entry means "field is present" - none of the seeded manga
    # have a synopsis, so this must return nothing
    response = await request_todo_manga_list(client, {"fields": ["-synopsis_en"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 0

    # Every seeded manga has a title_original, so the negative entry
    # (field present) matches all of them
    response = await request_todo_manga_list(client, {"fields": ["-title_original"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 4


async def test_todo_manga_list_filter_by_invalid_fields(client, aggregator_manga):
    response = await request_todo_manga_list(client, {"fields": ["bad-field"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_todo_manga_list_filter_by_media_type_list(client, aggregator_manga):
    response = await request_todo_manga_list(
        client, {"media_type": ["manga", "manhwa"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 3

    mal_ids = {entry["item"]["mal_id"] for entry in response.json()["list"]}

    assert mal_ids == {2, 25, 125036}


async def test_todo_manga_list_filter_by_status(client, aggregator_manga):
    response = await request_todo_manga_list(client, {"status": ["ongoing"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2

    mal_ids = {entry["item"]["mal_id"] for entry in response.json()["list"]}

    assert mal_ids == {2, 140765}


async def test_todo_manga_list_filter_by_years(client, aggregator_manga):
    response = await request_todo_manga_list(client, {"years": [2016, 2019]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2

    mal_ids = {entry["item"]["mal_id"] for entry in response.json()["list"]}

    assert mal_ids == {125036, 140765}


async def test_todo_manga_list_filter_by_invalid_years(client, aggregator_manga):
    response = await request_todo_manga_list(client, {"years": [2019, 2016]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


# These tests load aggregator_manga_info, which fills in most title/synopsis
# fields. To keep the facet filters (genres/magazines) under test from being
# coupled to the unrelated "any field missing" default fallback, they all
# pass `fields: ["-title_original"]` (title_original/title_ja is present for
# every seeded manga, unlike title_ua which stays missing for all of them)
# so the full 4-manga set stays in scope.


async def test_todo_manga_list_filter_by_genres(
    client, aggregator_genres, aggregator_manga, aggregator_manga_info
):
    # All four seeded manga have both adventure AND drama
    response = await request_todo_manga_list(
        client, {"genres": ["adventure", "drama"], "fields": ["-title_original"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 4

    # Excluding horror should filter out berserk only
    response = await request_todo_manga_list(
        client, {"genres": ["-horror"], "fields": ["-title_original"], "size": 20}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 3

    mal_ids = {entry["item"]["mal_id"] for entry in response.json()["list"]}

    assert 2 not in mal_ids


async def test_todo_manga_list_filter_by_magazines(
    client, aggregator_magazines, aggregator_manga, aggregator_manga_info
):
    response = await request_todo_manga_list(
        client,
        {"magazines": ["young-animal-4f9e5b"], "fields": ["-title_original"]},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["item"]["mal_id"] == 2


async def test_todo_manga_list_sort_by_start_date(client, aggregator_manga):
    response = await request_todo_manga_list(
        client, {"sort": ["start_date:desc"], "size": 20}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"][0]["item"]["mal_id"] == 140765
    assert response.json()["list"][-1]["item"]["mal_id"] == 2


async def test_todo_manga_list_sort_by_title(client, aggregator_manga):
    response = await request_todo_manga_list(
        client, {"sort": ["title_en:desc"], "size": 20}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"][0]["item"]["mal_id"] == 125036
    assert response.json()["list"][-1]["item"]["mal_id"] == 2


async def test_todo_manga_list_sort_by_media_type(client, aggregator_manga):
    response = await request_todo_manga_list(
        client, {"sort": ["media_type:asc"], "size": 20}
    )

    assert response.status_code == status.HTTP_200_OK
    media_types = [entry["item"]["media_type"] for entry in response.json()["list"]]

    assert media_types == sorted(media_types)
    assert response.json()["list"][-1]["item"]["mal_id"] == 125036

    response = await request_todo_manga_list(
        client, {"sort": ["media_type:desc"], "size": 20}
    )

    assert response.status_code == status.HTTP_200_OK
    media_types = [entry["item"]["media_type"] for entry in response.json()["list"]]

    assert media_types == sorted(media_types, reverse=True)
    assert response.json()["list"][0]["item"]["mal_id"] == 125036


async def test_todo_manga_list_sort_invalid(client, aggregator_manga):
    response = await request_todo_manga_list(client, {"sort": ["bad_field:asc"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"

    response = await request_todo_manga_list(client, {"sort": ["title_en:bad"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"
