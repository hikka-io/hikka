from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.models import Anime


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
