from sqlalchemy.orm import selectinload
from app.models import Franchise
from sqlalchemy import select
from sqlalchemy import func


async def test_import_anime_franchises(
    test_session,
    aggregator_anime,
    aggregator_anime_franchises,
):
    anime_franchises_count = await test_session.scalar(
        select(func.count(Franchise.id))
    )
    assert anime_franchises_count == 2

    # Check franchise
    franchise = await test_session.scalar(
        select(Franchise)
        .filter(Franchise.content_id == "4f17027c-2b0f-4ad5-b51e-3c4f729b16e1")
        .options(selectinload(Franchise.anime))
    )

    assert len(franchise.anime) == 3
