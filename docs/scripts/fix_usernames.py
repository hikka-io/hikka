from app.utils import get_settings, is_valid_username
from app.service import get_user_by_username
from app.database import sessionmanager
from app.service import create_log
from sqlalchemy import select
from app.models import User
from app import constants
import asyncio
import secrets
import sys
import re


def fix_username(username: str) -> str | None:
    """Replace forbidden characters or return None if username can't be fixed"""

    # Forbidden characters become underscores and leading ones are dropped
    # since username can't start with underscore
    fixed = re.sub(r"[^A-Za-z0-9_]", "_", username).lstrip("_")

    # Reserved, too short or letterless names can't be fixed this way
    return fixed if is_valid_username(fixed) else None


async def is_taken(session, username: str, taken: set[str]) -> bool:
    # Names picked earlier in this run count as taken too
    # since dry run doesn't save them to database
    if username.lower() in taken:
        return True

    return await get_user_by_username(session, username) is not None


async def pick_username(session, fixed: str | None, taken: set[str]) -> str:
    """Pick free username trying fixed name first"""

    if fixed:
        # Suffix takes 7 characters and username can't be longer than 64
        candidates = [fixed] + [
            f"{fixed[:57]}_{secrets.token_hex(3)}" for _ in range(5)
        ]

        for candidate in candidates:
            if not await is_taken(session, candidate, taken):
                return candidate

    # Same random username new oauth accounts get
    while True:
        username = f"user_{secrets.token_hex(6)}"

        if not await is_taken(session, username, taken):
            return username


async def fix_usernames(apply=False):
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        users = await session.execute(
            select(User.id, User.username).order_by(User.created)
        )

        bad_user_ids = [
            user.id for user in users if not is_valid_username(user.username)
        ]

        taken = set()
        stats = {"fixed": 0, "fixed with suffix": 0, "random": 0}

        for user_id in bad_user_ids:
            user = await session.get(User, user_id)

            before = user.username
            fixed = fix_username(before)
            after = await pick_username(session, fixed, taken)
            taken.add(after.lower())

            if fixed is None:
                result = "random"
            elif after == fixed:
                result = "fixed"
            else:
                result = "fixed with suffix"

            stats[result] += 1

            print(f"[{user.role}] {before!r} -> {after!r} ({result})")

            if not apply:
                continue

            # We don't touch last_username_change since that would stop
            # user from picking own username for an hour
            user.username = after
            user.needs_search_update = True

            # Same log as username change in settings, create_log commits
            await create_log(
                session,
                constants.LOG_SETTINGS_USERNAME,
                user,
                data={"before": before, "after": after, "system_edit": True},
            )

        print(
            f"Found {len(bad_user_ids)} bad usernames: "
            + ", ".join(f"{count} {result}" for result, count in stats.items())
        )

        if not apply:
            print("Dry run, pass --apply to save changes")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_usernames(apply="--apply" in sys.argv))
