from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload
from app.models import AnimeStaff
import math


async def update_anime_staff_weights(session):
    limit = 10000
    total = await session.scalar(select(func.count(AnimeStaff.id)))
    pages = math.ceil(total / limit) + 1

    for page in range(1, pages):
        offset = (limit * (page)) - limit

        staff_roles = await session.scalars(
            select(AnimeStaff)
            .options(selectinload(AnimeStaff.roles))
            .order_by(desc(AnimeStaff.id))
            .limit(limit)
            .offset(offset)
        )

        for staff in staff_roles:
            staff.weight = sum([role.weight for role in staff.roles])
            session.add(staff)

        await session.commit()
