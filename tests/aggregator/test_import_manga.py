from sqlalchemy import select
from app.models import Manga
from sqlalchemy import func


async def test_import_manga(test_session, aggregator_manga):
    manga_count = await test_session.scalar(select(func.count(Manga.id)))
    assert manga_count == 4

    # Check individual manga
    manga = await test_session.scalar(
        select(Manga).filter(Manga.slug == "fullmetal-alchemist-7ef8d2")
    )

    assert manga is not None
    assert manga.title_original == "Fullmetal Alchemist"
    assert manga.needs_search_update is True
    assert manga.mal_id == 25
