from client_requests import request_manga_search
from fastapi import status


async def test_manga_list(
    client,
    aggregator_manga,
    aggregator_manga_info,
):
    # Make request to manga list
    response = await request_manga_search(client)

    assert response.status_code == status.HTTP_200_OK

    # Check pagination data
    assert response.json()["pagination"]["total"] == 4
    assert response.json()["pagination"]["pages"] == 1
    assert response.json()["pagination"]["page"] == 1

    # Check first manga slug
    assert response.json()["list"][0]["slug"] == "berserk-fb9fbd"

    # Check last manga slug
    assert response.json()["list"][3]["slug"] == "the-horizon-f9ebc0"


async def test_manga_list_extra_fields(
    client,
    aggregator_genres,
    aggregator_magazines,
    aggregator_manga,
    aggregator_manga_info,
):
    # Catalog entries should expose genres, magazines and synopsis fields
    response = await request_manga_search(client)

    assert response.status_code == status.HTTP_200_OK

    manga = response.json()["list"][0]
    assert manga["slug"] == "berserk-fb9fbd"

    genre_slugs = sorted(genre["slug"] for genre in manga["genres"])
    assert genre_slugs == [
        "action",
        "adventure",
        "award-winning",
        "drama",
        "fantasy",
        "gore",
        "horror",
        "military",
        "mythology",
        "psychological",
        "supernatural",
    ]

    assert manga["genres"][0]["name_en"] is not None

    assert [magazine["slug"] for magazine in manga["magazines"]] == [
        "young-animal-4f9e5b"
    ]
    assert manga["magazines"][0]["name_en"] == "Young Animal"

    # Both synopsis fields must be present in the catalog response
    assert "synopsis_en" in manga
    assert "synopsis_ua" in manga
    assert manga["synopsis_en"] is not None
