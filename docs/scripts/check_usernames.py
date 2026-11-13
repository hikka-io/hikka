from app.utils import is_protected_username
from app.database import sessionmanager
from app.models import User, UserOAuth
from app.utils import get_settings
from collections import Counter
from sqlalchemy import select
import asyncio
import re

USERNAME_PATTERN = "^[A-Za-z0-9][A-Za-z0-9_]{4,63}$"


def is_valid_username(username: str) -> bool:
    """Check username against same rules as signup and username change"""

    return (
        re.fullmatch(USERNAME_PATTERN, username) is not None
        and any(char.isalpha() for char in username)
        and not is_protected_username(username)
    )


def username_problems(username: str) -> dict[str, str]:
    """Explain which username rules are broken keyed by issue type"""

    problems = {}

    if not 5 <= len(username) <= 64:
        problems["wrong length"] = f"length {len(username)}"

    if not re.match(r"[A-Za-z0-9]", username):
        problems["bad first character"] = f"starts with {username[:1]!r}"

    if not re.search(r"[A-Za-z]", username):
        problems["no letters"] = "no letters"

    if bad_characters := sorted(set(re.sub(r"[A-Za-z0-9_]", "", username))):
        problems["bad characters"] = f"characters {''.join(bad_characters)!r}"

    if is_protected_username(username):
        problems["reserved"] = "reserved"

    return problems


async def check_usernames():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        oauth_user_ids = set(await session.scalars(select(UserOAuth.user_id)))

        users = await session.execute(
            select(User.id, User.username, User.role, User.created).order_by(
                User.created
            )
        )

        checked = 0
        found = Counter()
        issues = Counter()

        for user in users:
            checked += 1

            # Same rules as signup and username change
            if is_valid_username(user.username):
                continue

            source = "oauth" if user.id in oauth_user_ids else "regular"
            problems = username_problems(user.username)
            issues.update(problems.keys())
            found[source] += 1

            print(
                f"[{user.role}] {user.username!r} ({source}, "
                f"created {user.created:%Y-%m-%d}): "
                f"{', '.join(problems.values())}"
            )

        print(
            f"Checked {checked} users, found {sum(found.values())} bad usernames "
            f"({found['oauth']} oauth, {found['regular']} regular)"
        )

        # Username can break several rules so counts may add up to more
        for issue, count in issues.most_common():
            print(f"  {issue}: {count}")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(check_usernames())
