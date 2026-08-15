from client_requests import request_todo_anime_list
from fastapi import status


async def test_todo_anime_list(client, aggregator_anime):
    # None of the seeded anime have a synopsis, so all of them show up
    # as having issues by default
    response = await request_todo_anime_list(client)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 17
    assert len(response.json()["list"]) == 15


async def test_todo_anime_list_search_no_meilisearch(client, aggregator_anime):
    # When Meilisearch is down search should throw query down error
    response = await request_todo_anime_list(client, {"query": "test"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "search:query_down"


async def test_todo_anime_list_search_invalid_query(client, aggregator_anime):
    response = await request_todo_anime_list(client, {"query": "a"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_todo_anime_list_filter_by_mal_id(client, aggregator_anime):
    response = await request_todo_anime_list(client, {"mal_id": 47917})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["item"]["slug"] == "bocchi-the-rock-9e172d"


async def test_todo_anime_list_filter_by_media_type(client, aggregator_anime):
    response = await request_todo_anime_list(client, {"media_type": ["movie"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2

    mal_ids = {entry["item"]["mal_id"] for entry in response.json()["list"]}

    assert mal_ids == {32281, 216}


async def test_todo_anime_list_filter_by_fields(client, aggregator_anime):
    # Every seeded anime already has a title_original, so filtering for
    # anime missing one should return nothing
    response = await request_todo_anime_list(client, {"fields": ["title_original"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 0

    response = await request_todo_anime_list(client, {"fields": ["synopsis_en"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 17

    # Negative entry means "field is present" - none of the seeded anime
    # have a synopsis, so this must return nothing
    response = await request_todo_anime_list(client, {"fields": ["-synopsis_en"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 0

    # Every seeded anime has a title_original, so the negative entry
    # (field present) matches all of them
    response = await request_todo_anime_list(client, {"fields": ["-title_original"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 17


async def test_todo_anime_list_filter_by_invalid_fields(client, aggregator_anime):
    response = await request_todo_anime_list(client, {"fields": ["bad-field"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


async def test_todo_anime_list_filter_by_media_type_list(client, aggregator_anime):
    response = await request_todo_anime_list(
        client, {"media_type": ["movie", "ova"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 3

    mal_ids = {entry["item"]["mal_id"] for entry in response.json()["list"]}

    assert mal_ids == {32281, 216, 10851}


async def test_todo_anime_list_filter_by_status(client, aggregator_anime):
    response = await request_todo_anime_list(client, {"status": ["ongoing"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["item"]["mal_id"] == 51535


async def test_todo_anime_list_filter_by_season(client, aggregator_anime):
    response = await request_todo_anime_list(client, {"season": ["summer"]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 2

    mal_ids = {entry["item"]["mal_id"] for entry in response.json()["list"]}

    assert mal_ids == {32281, 35760}


async def test_todo_anime_list_filter_by_years(client, aggregator_anime):
    response = await request_todo_anime_list(client, {"years": [2020, 2022]})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 5

    mal_ids = {entry["item"]["mal_id"] for entry in response.json()["list"]}

    assert mal_ids == {43608, 40591, 40028, 48583, 47917}


async def test_todo_anime_list_filter_by_invalid_years(client, aggregator_anime):
    response = await request_todo_anime_list(client, {"years": [2022, 2020]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"


# These tests load aggregator_anime_info, which fills in most title/synopsis
# fields. To keep the facet filters (rating/genres/studios) under test from
# being coupled to the unrelated "any field missing" default fallback, they
# all pass `fields: ["-title_original"]` (title_original/title_ja is present
# for every seeded anime, unlike title_ua/synopsis_ua which go missing for
# a couple of entries) so the full 17-anime set stays in scope.


async def test_todo_anime_list_filter_by_rating(
    client, aggregator_anime, aggregator_anime_info
):
    response = await request_todo_anime_list(
        client, {"rating": ["rx"], "fields": ["-title_original"]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 1
    assert response.json()["list"][0]["item"]["mal_id"] == 10851


async def test_todo_anime_list_filter_by_genres(
    client, aggregator_genres, aggregator_anime, aggregator_anime_info
):
    # Both entries have comedy AND romance
    response = await request_todo_anime_list(
        client, {"genres": ["comedy", "romance"], "fields": ["-title_original"]}
    )

    assert response.status_code == status.HTTP_200_OK

    mal_ids = {entry["item"]["mal_id"] for entry in response.json()["list"]}

    assert mal_ids == {43608, 216}

    # Excluding hentai should filter out euphoria only
    response = await request_todo_anime_list(
        client, {"genres": ["-hentai"], "fields": ["-title_original"], "size": 20}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pagination"]["total"] == 16

    mal_ids = {entry["item"]["mal_id"] for entry in response.json()["list"]}

    assert 10851 not in mal_ids


async def test_todo_anime_list_filter_by_studios(
    client, aggregator_companies, aggregator_anime, aggregator_anime_info
):
    response = await request_todo_anime_list(
        client, {"studios": ["bones-b0b61b"], "fields": ["-title_original"]}
    )

    assert response.status_code == status.HTTP_200_OK

    mal_ids = {entry["item"]["mal_id"] for entry in response.json()["list"]}

    assert 5114 in mal_ids


async def test_todo_anime_list_sort_by_start_date(client, aggregator_anime):
    response = await request_todo_anime_list(
        client, {"sort": ["start_date:desc"], "size": 20}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"][0]["item"]["mal_id"] == 52034
    assert response.json()["list"][-1]["item"]["mal_id"] == 216


async def test_todo_anime_list_sort_by_title(client, aggregator_anime):
    # Euphoria has no title_en, so on a desc sort nulls must come last
    response = await request_todo_anime_list(
        client, {"sort": ["title_en:desc"], "size": 20}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["list"][-1]["item"]["mal_id"] == 10851


async def test_todo_anime_list_sort_by_media_type(client, aggregator_anime):
    response = await request_todo_anime_list(
        client, {"sort": ["media_type:asc"], "size": 20}
    )

    assert response.status_code == status.HTTP_200_OK
    media_types = [entry["item"]["media_type"] for entry in response.json()["list"]]

    assert media_types == sorted(media_types)
    assert media_types[0] == "movie"
    assert media_types[-1] == "tv"

    response = await request_todo_anime_list(
        client, {"sort": ["media_type:desc"], "size": 20}
    )

    assert response.status_code == status.HTTP_200_OK
    media_types = [entry["item"]["media_type"] for entry in response.json()["list"]]

    assert media_types == sorted(media_types, reverse=True)
    assert media_types[0] == "tv"
    assert media_types[-1] == "movie"


async def test_todo_anime_list_sort_invalid(client, aggregator_anime):
    response = await request_todo_anime_list(client, {"sort": ["bad_field:asc"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"

    response = await request_todo_anime_list(client, {"sort": ["title_en:bad"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "system:validation_error"
