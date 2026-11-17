from app.sync.aggregator.anime import aggregator_anime
from datetime import datetime
from sqlalchemy import select
from app.models import Anime
from sqlalchemy import func
from unittest import mock
import helpers


async def test_import_anime(test_session, aggregator_anime):
    anime_count = await test_session.scalar(select(func.count(Anime.id)))
    assert anime_count == 17

    # Check individual anime
    anime = await test_session.scalar(
        select(Anime).filter(
            Anime.slug == "fullmetal-alchemist-brotherhood-fc524a"
        )
    )

    assert anime is not None
    assert anime.created == datetime(2023, 6, 20, 15, 7, 22)
    assert anime.title_ja == "Fullmetal Alchemist: Brotherhood"
    assert anime.needs_search_update is True
    assert anime.mal_id == 5114
    assert anime.image is None

    # Poster from the list is saved as system image
    anime = await test_session.scalar(
        select(Anime).filter(Anime.slug == "steinsgate-f29797")
    )

    assert anime.image_relation.system is True
    assert (
        anime.image_relation.path
        == "/content/anime/steinsgate-f29797/M-8Gxbqmsq0ScxFZWQAt-Q.jpg"
    )


async def test_import_anime_pages(test_session):
    data = await helpers.load_json("tests/data/anime.json")

    # Serve the 17 fixture entries as 3 pages
    pages = [data["list"][0:6], data["list"][6:12], data["list"][12:]]
    requested = []

    async def request_aggregator(path):
        requested.append(path)
        page = int(path.split("page=")[1])

        return {
            "pagination": {"pages": len(pages), "page": page},
            "list": pages[page - 1],
        }

    with mock.patch(
        "app.sync.aggregator.requests.request_aggregator", request_aggregator
    ):
        await aggregator_anime()

    # Every page is fetched once
    assert sorted(requested) == [
        "/anime?page=1",
        "/anime?page=2",
        "/anime?page=3",
    ]

    anime_count = await test_session.scalar(select(func.count(Anime.id)))
    assert anime_count == 17
