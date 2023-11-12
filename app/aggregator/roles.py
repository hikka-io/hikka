from app.models import AnimeStaffRole
from sqlalchemy import select
from app import utils


async def update_anime_roles(session, data):
    create_roles = []

    for role_name in data:
        slug = utils.slugify(role_name)

        if await session.scalar(
            select(AnimeStaffRole).filter(AnimeStaffRole.slug == slug)
        ):
            continue

        role = AnimeStaffRole(
            **{
                "name_en": role_name,
                "slug": slug,
            }
        )

        create_roles.append(role)

        print(f"Added anime staff role: {role.name_en}")

    session.add_all(create_roles)
    await session.commit()
