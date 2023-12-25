from app.models import AnimeStaffRole
from sqlalchemy import select
from app import utils
import aiofiles
import json


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

        # print(f"Added anime staff role: {role.name_en}")

    session.add_all(create_roles)
    await session.commit()


# This is bit hacky but works
# ToDo: remove this (?)
async def update_anime_role_weights(session):
    async with aiofiles.open("docs/roles.json", mode="r") as file:
        contents = await file.read()
        data = json.loads(contents)

        for entry in data["service_content_anime_staff_roles"]:
            role = await session.scalar(
                select(AnimeStaffRole).filter(
                    AnimeStaffRole.slug == entry["slug"]
                )
            )

            if role.weight:
                continue

            role.name_ua = entry["name_ua"]
            role.weight = entry["weight"]

            session.add(role)

        await session.commit()
