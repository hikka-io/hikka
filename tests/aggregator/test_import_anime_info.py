from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.models import Anime
from app import aggregator
import helpers


async def test_import_anime_info(
    test_session,
    aggregator_anime_genres,
    aggregator_anime,
    aggregator_people,
    aggregator_characters,
    aggregator_anime_roles,
    aggregator_anime_info,
):
    # Check individual anime
    anime = await test_session.scalar(
        select(Anime)
        .filter(Anime.slug == "fullmetal-alchemist-brotherhood-fc524a")
        .options(selectinload(Anime.genres))
        .options(selectinload(Anime.episodes_list))
        .options(selectinload(Anime.voices))
        .options(selectinload(Anime.staff))
    )

    assert anime is not None
    assert anime.synopsis_ua is not None

    assert len(anime.genres) == 5
    assert len(anime.episodes_list) == 64
    assert len(anime.voices) == 191
    assert len(anime.staff) == 78


async def test_import_anime_info_ignored_fields(
    test_session,
    aggregator_anime,
    aggregator_anime_info,
):
    # Check individual anime
    anime = await test_session.scalar(
        select(Anime).filter(
            Anime.slug == "fullmetal-alchemist-brotherhood-fc524a"
        )
    )

    anime.title_en = "Changed title"
    anime.ignored_fields.append("title_en")

    test_session.add(anime)
    await test_session.commit()

    data = await helpers.load_json("tests/data/anime_info/fma.json")
    await aggregator.update_anime_info(test_session, anime, data)

    await test_session.refresh(anime)
    assert anime.title_en == "Changed title"
