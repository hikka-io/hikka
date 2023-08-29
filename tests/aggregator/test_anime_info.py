from sqlalchemy import select
from app.models import Anime


async def test_import_anime_info(
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

    assert anime is not None
    assert anime.synopsis_ua is not None

    # ToDo: add more checks here (genres/episodes/etc)
