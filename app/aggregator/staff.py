from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from app.models import AnimeStaff


async def update_anime_staff_weights(session):
    count = await session.scalar(
        select(func.count(AnimeStaff.id)).filter(
            AnimeStaff.weight == None  # noqa: E711
        )
    )

    while count > 0:
        staff_roles = await session.scalars(
            select(AnimeStaff)
            .options(selectinload(AnimeStaff.roles))
            .limit(20000)
        )

        for staff in staff_roles:
            staff.weight = sum([role.weight for role in staff.roles])
            session.add(staff)

        await session.commit()

        count = await session.scalar(
            select(func.count(AnimeStaff.id)).filter(
                AnimeStaff.weight == None  # noqa: E711
            )
        )
