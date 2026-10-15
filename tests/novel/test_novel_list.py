from client_requests import request_novel_search
from fastapi import status


async def test_novel_list(
    client,
    aggregator_novel,
    aggregator_novel_info,
):
    # Make request to novel list
    response = await request_novel_search(client)

    assert response.status_code == status.HTTP_200_OK

    # Check pagination data
    assert response.json()["pagination"]["total"] == 2
    assert response.json()["pagination"]["pages"] == 1
    assert response.json()["pagination"]["page"] == 1

    # Check first novel slug
    assert response.json()["list"][0]["slug"] == "tian-guan-cifu-7bb159"

    # Check last novel slug
    assert (
        response.json()["list"][1]["slug"]
        == "kono-subarashii-sekai-ni-shukufuku-wo-cc5525"
    )


async def test_novel_list_extra_fields(
    client,
    aggregator_genres,
    aggregator_magazines,
    aggregator_novel,
    aggregator_novel_info,
):
    # Catalog entries should expose genres, magazines and synopsis fields
    response = await request_novel_search(client)

    assert response.status_code == status.HTTP_200_OK

    novel = response.json()["list"][0]
    assert novel["slug"] == "tian-guan-cifu-7bb159"

    assert sorted(genre["slug"] for genre in novel["genres"]) == [
        "action",
        "adventure",
        "boys-love",
        "supernatural",
    ]

    assert novel["genres"][0]["name_en"] is not None
    assert novel["genres"][0]["type"] == "genre"

    # None of the novels in test data have magazines attached,
    # but the field must still be exposed
    assert novel["magazines"] == []

    # Both synopsis fields must be present in the catalog response
    assert "synopsis_en" in novel
    assert "synopsis_ua" in novel
    assert novel["synopsis_en"] is not None


async def test_novel_search_query_pagination(
    client, mock_meilisearch, aggregator_novel, aggregator_novel_info
):
    # Meilisearch returns second page out of 40 results
    mock_meilisearch.hits = [
        "7bb1594b-9a84-4632-948d-594903e85676",
        "cc552518-5e42-43fa-a729-0f9a81db5767",
    ]
    mock_meilisearch.total = 40

    response = await request_novel_search(
        client, {"query": "novel"}, page=2, size=2
    )

    assert response.status_code == status.HTTP_200_OK
    assert mock_meilisearch.calls[0]["page"] == 2

    # Total comes from Meilisearch and page is not offset second time
    assert response.json()["pagination"]["total"] == 40
    assert response.json()["pagination"]["pages"] == 20
    assert response.json()["pagination"]["page"] == 2
    assert len(response.json()["list"]) == 2
