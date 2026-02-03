from app.common.utils import is_valid_css_background
from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select
from app.models import User
import asyncio
import copy


async def fix_collection_comments():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        users = await session.scalars(select(User))

        for user in users:
            fixed_bg = False

            for theme_color in ["light", "dark"]:
                if user.styles is None:
                    continue

                if (
                    theme_color not in user.styles
                    or user.styles[theme_color] is None
                ):
                    continue

                if (
                    "body" not in user.styles[theme_color]
                    or user.styles[theme_color]["body"] is None
                ):
                    continue

                if "background_image" not in user.styles[theme_color]["body"]:
                    continue

                if not is_valid_css_background(
                    user.styles[theme_color]["body"]["background_image"]
                ):
                    user.styles = copy.deepcopy(user.styles)
                    user.styles[theme_color]["body"]["background_image"] = None
                    fixed_bg = True

            if fixed_bg:
                print(f"Fixed background for {user.username}")

        # await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_collection_comments())
