from app.database import sessionmanager
from app.models import Anime, Edit
from app.utils import get_settings
from sqlalchemy import select, or_
from app import constants
import asyncio
import sys

FIELDS = ["episodes_released", "status"]


async def get_moderated(session, field):
    return set(
        await session.scalars(
            select(Edit.content_id).filter(
                Edit.content_type == constants.CONTENT_ANIME,
                Edit.status == constants.EDIT_ACCEPTED,
                Edit.system_edit == False,  # noqa: E712
                Edit.after.has_key(field),
            )
        )
    )


async def fix_schedule_ignored_fields(apply=False):
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        moderated = {
            field: await get_moderated(session, field) for field in FIELDS
        }

        anime_list = await session.scalars(
            select(Anime).filter(
                or_(*[Anime.ignored_fields.has_key(field) for field in FIELDS])
            )
        )

        unlocked = {field: 0 for field in FIELDS}
        kept = {field: 0 for field in FIELDS}
        refresh = 0

        for anime in anime_list:
            ignored_fields = list(anime.ignored_fields)

            for field in FIELDS:
                if field not in ignored_fields:
                    continue

                # Keep fields changed by moderators
                if anime.id in moderated[field]:
                    kept[field] += 1
                    continue

                ignored_fields.remove(field)
                unlocked[field] += 1

            if ignored_fields == list(anime.ignored_fields):
                continue

            # Pick up current MAL values on next sync
            needs_update = anime.status != constants.RELEASE_STATUS_FINISHED
            refresh += int(needs_update)

            if apply:
                anime.ignored_fields = ignored_fields

                if needs_update:
                    anime.needs_update = True

        for field in FIELDS:
            print(
                f"{field}: unlocked {unlocked[field]}, "
                f"kept {kept[field]} set by moderators"
            )

        print(f"Anime to refresh from aggregator: {refresh}")

        if apply:
            await session.commit()
            print("Changes saved")

        else:
            print("Dry run, pass --apply to save changes")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_schedule_ignored_fields(apply="--apply" in sys.argv))
