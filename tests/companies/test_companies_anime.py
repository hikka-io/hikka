from client_requests import request_companies_anime
from sqlalchemy.orm import selectinload
from app.models import Company
from sqlalchemy import select
from fastapi import status


async def test_companies_anime(
    client,
    aggregator_companies,
    aggregator_anime,
    aggregator_anime_info,
):
    # Get anime produced by Bones
    response = await request_companies_anime(client, "bones-b0b61b")

    assert response.status_code == status.HTTP_200_OK

    # Check slugs
    assert response.json()["list"][0]["type"] == "studio"
    assert (
        response.json()["list"][0]["anime"]["slug"]
        == "fullmetal-alchemist-brotherhood-fc524a"
    )

    assert response.json()["list"][1]["type"] == "producer"
    assert (
        response.json()["list"][1]["anime"]["slug"]
        == "pia-carrot-e-youkoso-sayaka-no-koi-monogatari-227414"
    )


async def test_companies_anime_filter(
    client,
    aggregator_companies,
    aggregator_anime,
    aggregator_anime_info,
    test_session,
):
    # Get anime produced by Bones (studio)
    response = await request_companies_anime(client, "bones-b0b61b", "studio")

    assert response.status_code == status.HTTP_200_OK

    # Check data
    assert len(response.json()["list"]) == 1

    assert response.json()["list"][0]["type"] == "studio"
    assert (
        response.json()["list"][0]["anime"]["slug"]
        == "fullmetal-alchemist-brotherhood-fc524a"
    )

    # Get anime produced by Bones (producer)
    response = await request_companies_anime(client, "bones-b0b61b", "producer")

    assert response.status_code == status.HTTP_200_OK

    # Check data
    assert len(response.json()["list"]) == 1

    assert response.json()["list"][0]["type"] == "producer"
    assert (
        response.json()["list"][0]["anime"]["slug"]
        == "pia-carrot-e-youkoso-sayaka-no-koi-monogatari-227414"
    )

    # Company relationships should load the same anime
    company = await test_session.scalar(
        select(Company)
        .filter(Company.slug == "bones-b0b61b")
        .options(
            selectinload(Company.studio_anime),
            selectinload(Company.produced_anime),
        )
    )

    assert [anime.slug for anime in company.studio_anime] == [
        "fullmetal-alchemist-brotherhood-fc524a"
    ]

    assert [anime.slug for anime in company.produced_anime] == [
        "pia-carrot-e-youkoso-sayaka-no-koi-monogatari-227414"
    ]
