from app.models import AnimeFranchise
from sqlalchemy import select
from sqlalchemy import func


async def test_import_anime_franchises(
    test_session,
    aggregator_anime,
    aggregator_anime_franchises,
):
    anime_franchises_count = await test_session.scalar(
        select(func.count(AnimeFranchise.id))
    )
    assert anime_franchises_count == 100

    # ToDo: add more checks
