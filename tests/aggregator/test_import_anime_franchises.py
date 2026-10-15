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

    # Aggregator sent no entries for this one
    assert franchise.relations == []

    # Check relations for SNK
    franchise = await test_session.scalar(
        select(Franchise).filter(
            Franchise.content_id == "e2283d58-ba06-420e-92de-8fe597d69a02"
        )
    )

    relations = {
        (
            relation["content_id"],
            relation["related_content_id"],
            relation["relation_type"],
        )
        for relation in franchise.relations
    }

    # Each pair is stored once and other relation is ignored
    assert len(franchise.relations) == 7
    assert relations == {
        # Both sides agree
        (
            "0cf69ac6-9238-4e2f-9add-39294c1a0f11",
            "b88bf4b4-564e-43d4-8f1a-01741d244366",
            "sequel",
        ),
        # Only one side lists it
        (
            "b88bf4b4-564e-43d4-8f1a-01741d244366",
            "b22bb359-4545-45ce-92d3-df8646554128",
            "sequel",
        ),
        # Parent story gets exact type from the other side
        (
            "b22bb359-4545-45ce-92d3-df8646554128",
            "91a35018-3439-47b1-8eb8-ba2092fd0191",
            "sequel",
        ),
        (
            "91a35018-3439-47b1-8eb8-ba2092fd0191",
            "4877caaf-d76d-46f2-9a73-cbdb2fef202b",
            "sequel",
        ),
        # Both sides say sequel, lower MAL id becomes source
        (
            "4877caaf-d76d-46f2-9a73-cbdb2fef202b",
            "8d3fc3a7-1fa5-4ce4-909f-3d60ca2d072e",
            "sequel",
        ),
        (
            "8d3fc3a7-1fa5-4ce4-909f-3d60ca2d072e",
            "833be1cc-b3ef-4ebc-8017-07f49203a8a0",
            "sequel",
        ),
        # Manga we don't have is still stored
        (
            "0cf69ac6-9238-4e2f-9add-39294c1a0f11",
            "c5a7e2d4-3f1b-4e8a-9b6d-2a1f0e9c8b7d",
            "adaptation",
        ),
    }
