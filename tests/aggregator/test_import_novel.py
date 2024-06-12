from sqlalchemy import select
from app.models import Novel
from sqlalchemy import func


async def test_import_novel(test_session, aggregator_novel):
    novel_count = await test_session.scalar(select(func.count(Novel.id)))
    assert novel_count == 2

    # Check individual novel
    novel = await test_session.scalar(
        select(Novel).filter(
            Novel.slug == "kono-subarashii-sekai-ni-shukufuku-wo-cc5525"
        )
    )

    assert novel is not None
    assert novel.title_original == "Kono Subarashii Sekai ni Shukufuku wo!"
    assert novel.needs_search_update is True
    assert novel.mal_id == 60553
