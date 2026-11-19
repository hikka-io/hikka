from sqlalchemy.orm import selectinload
from app.models import Franchise, Anime
from sqlalchemy import select
from sqlalchemy import func
from app import aggregator
import helpers


async def count_franchise_anime(session, content_id):
    return await session.scalar(
        select(func.count(Anime.id))
        .join(Franchise, Anime.franchise_id == Franchise.id)
        .filter(Franchise.content_id == content_id)
    )


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

    # Aggregator moves titles out of franchises
    data = await helpers.load_json("tests/data/anime_franchises.json")
    franchises = {entry["content_id"]: entry for entry in data["list"]}

    first = franchises["4f17027c-2b0f-4ad5-b51e-3c4f729b16e1"]
    snk = franchises["e2283d58-ba06-420e-92de-8fe597d69a02"]

    lost_id = first["franchise_entries"][2]["content_id"]
    moved_id = snk["franchise_entries"][0]["content_id"]

    # One title is no longer listed
    first["franchise_entries"] = first["franchise_entries"][:2]
    first["updated"] += 60

    # One title is split off into new franchise
    split = {
        **snk,
        "content_id": "split-off-franchise",
        "franchise_entries": snk["franchise_entries"][:1],
        "entries": [],
        "updated": snk["updated"] + 60,
    }

    # Rest of franchise is emptied
    snk["franchise_entries"] = []
    snk["entries"] = []
    snk["updated"] += 60

    # Split franchise goes first and emptied one must not detach moved title
    await aggregator.save_franchises_list(test_session, [first, split, snk])

    # Queried directly since session keeps objects loaded before sync
    assert await count_franchise_anime(test_session, first["content_id"]) == 2
    assert await count_franchise_anime(test_session, split["content_id"]) == 1
    assert await count_franchise_anime(test_session, snk["content_id"]) == 0

    lost_franchise_id = await test_session.scalar(
        select(Anime.franchise_id).filter(Anime.content_id == lost_id)
    )

    assert lost_franchise_id is None

    moved_franchise = await test_session.scalar(
        select(Franchise.content_id)
        .join(Anime, Anime.franchise_id == Franchise.id)
        .filter(Anime.content_id == moved_id)
    )

    assert moved_franchise == split["content_id"]

    snk_relations = await test_session.scalar(
        select(Franchise.relations).filter(
            Franchise.content_id == snk["content_id"]
        )
    )

    assert snk_relations == []
