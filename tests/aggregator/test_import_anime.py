from sqlalchemy import select
from app.models import Anime
from sqlalchemy import func


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
    assert anime.title_ja == "Fullmetal Alchemist: Brotherhood"
