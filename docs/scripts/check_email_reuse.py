from app.common.auth.service import normalize_email
from app.database import sessionmanager
from app.models import User, UserOAuth
from collections import defaultdict
from app.utils import get_settings
from collections import Counter
from sqlalchemy import select
from app import constants
import asyncio


def alias_reasons(email: str) -> list[str]:
    """Explain why email differs from its normalized form"""

    email = email.strip().lower()
    local, _, domain = email.partition("@")
    reasons = []

    if domain in constants.EMAIL_PLUS_DOMAINS and "+" in local:
        reasons.append("plus label")

    if (
        domain in constants.EMAIL_GMAIL_DOMAINS
        and "." in local.split("+", 1)[0]
    ):
        reasons.append("gmail dots")

    if domain == "googlemail.com":
        reasons.append("googlemail domain")

    return reasons


async def check_email_reuse():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        oauth_user_ids = set(await session.scalars(select(UserOAuth.user_id)))

        users = await session.execute(
            select(User.id, User.username, User.email, User.role, User.created)
            .filter(User.email != None)  # noqa: E711
            .order_by(User.created)
        )

        groups = defaultdict(list)
        checked = 0

        for user in users:
            checked += 1
            groups[normalize_email(user.email)].append(user)

        reused = {
            email: accounts
            for email, accounts in groups.items()
            if len(accounts) > 1
        }

        reasons = Counter()
        sources = Counter()
        domains = Counter()

        for email, accounts in sorted(
            reused.items(), key=lambda item: len(item[1]), reverse=True
        ):
            domains[email.partition("@")[2]] += 1

            print(f"{email}: {len(accounts)} accounts")

            for user in accounts:
                source = "oauth" if user.id in oauth_user_ids else "regular"
                user_reasons = alias_reasons(user.email)
                reasons.update(user_reasons or ["same address"])
                sources[source] += 1

                print(
                    f"  [{user.role}] {user.username!r} <{user.email}> "
                    f"({source}, created {user.created:%Y-%m-%d})"
                    + (f": {', '.join(user_reasons)}" if user_reasons else "")
                )

        accounts_total = sum(len(accounts) for accounts in reused.values())

        print(
            f"Checked {checked} users with email, {len(reused)} mailboxes "
            f"are used by {accounts_total} accounts "
            f"({accounts_total - len(reused)} extra accounts)"
        )

        print(f"  oauth accounts: {sources['oauth']}")
        print(f"  regular accounts: {sources['regular']}")

        # Address can use several tricks at once so counts may add up to more
        print("By alias type:")
        for reason, count in reasons.most_common():
            print(f"  {reason}: {count}")

        print("By domain:")
        for domain, count in domains.most_common(10):
            print(f"  {domain}: {count}")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(check_email_reuse())
