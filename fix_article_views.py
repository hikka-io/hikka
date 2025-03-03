from app.sync import update_article_views
import asyncio


async def fix_article_views():
    await update_article_views()


if __name__ == "__main__":
    asyncio.run(fix_article_views())
