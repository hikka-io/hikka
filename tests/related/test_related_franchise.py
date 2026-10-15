from client_requests import request_related_franchise
from fastapi import status


async def test_related_franchise(
    client,
    aggregator_anime,
    aggregator_anime_franchises,
):
    response = await request_related_franchise(
        client, "anime", "shingeki-no-kyojin-0cf69a"
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["anime"]) == 7

    # Relations reference entries by slug so map them back to MAL ids
    mal_ids = {
        anime["slug"]: anime["mal_id"] for anime in response.json()["anime"]
    }

    relations = {
        (
            mal_ids[relation["slug"]],
            mal_ids[relation["related_slug"]],
            relation["relation_type"],
        )
        for relation in response.json()["relations"]
    }

    # Adaptation to manga we don't have is not returned
    assert len(response.json()["relations"]) == 6
    assert relations == {
        (16498, 25777, "sequel"),
        (25777, 35760, "sequel"),
        (35760, 38524, "sequel"),
        (38524, 40028, "sequel"),
        (40028, 48583, "sequel"),
        (48583, 51535, "sequel"),
    }

    assert all(
        relation["content_type"] == "anime"
        and relation["related_content_type"] == "anime"
        for relation in response.json()["relations"]
    )


async def test_related_franchise_no_relations(
    client,
    aggregator_anime,
    aggregator_anime_franchises,
):
    # Franchise without entries from aggregator still works
    response = await request_related_franchise(
        client,
        "anime",
        "kaguya-sama-wa-kokurasetai-tensai-tachi-no-renai-zunousen-a3ac07",
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["anime"]) == 3
    assert response.json()["relations"] == []
