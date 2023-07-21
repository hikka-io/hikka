from app.database import sessionmanager
from app.models import AnimeStaffRole
from sqlalchemy import select
from . import requests
from app import utils
import config


async def aggregator_anime_roles():
    sessionmanager.init(config.database)

    async with sessionmanager.session() as session:
        data = await requests.get_anime_roles()
        create_roles = []

        for role_name in data:
            slug = utils.slugify(role_name)

            if await session.scalar(
                select(AnimeStaffRole).filter_by(slug=slug)
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
