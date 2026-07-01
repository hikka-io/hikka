from app.database import sessionmanager
from app.models import Character
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import func, or_


async def resolve_orphaned_characters(session):
    await session.execute(
        update(Character)
        .values(
            needs_search_update=True,
            orphan=True,
        )
        .filter(
            Character.orphan == False,  # noqa: E712
            ~Character.anime.any(),
            ~Character.manga.any(),
            ~Character.novel.any(),
        )
    )

    await session.execute(
        update(Character)
        .values(
            needs_search_update=True,
            orphan=False,
        )
        .filter(
            Character.orphan == True,  # noqa: E712
            or_(
                Character.anime.any(),
                Character.manga.any(),
                Character.novel.any(),
            ),
        )
    )

    await session.commit()

    orphan_count = await session.scalar(
        select(func.count(Character.id)).filter(
            Character.orphan == True,  # noqa: E712
        )
    )

    print(f"Marked {orphan_count} characters as orphaned")


async def update_orphans():
    async with sessionmanager.session() as session:
        await resolve_orphaned_characters(session)
