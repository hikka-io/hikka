from pydantic import TypeAdapter, ValidationError, HttpUrl
from app.common.schemas.document import DocumentLinkUrl
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from app.utils import get_settings
from app.models import Article
from sqlalchemy import select
import asyncio


# Same validation document schema uses for links, images and videos
link_url = TypeAdapter(DocumentLinkUrl)
http_url = TypeAdapter(HttpUrl)


def find_urls(nodes):
    """Yield type and url of every node with url in document tree"""

    for node in nodes:
        if not isinstance(node, dict):
            continue

        if "url" in node:
            yield node.get("type"), node["url"]

        yield from find_urls(node.get("children") or [])


def is_valid_url(node_type, url):
    adapter = link_url if node_type == "a" else http_url

    try:
        adapter.validate_python(url)
        return True

    except ValidationError:
        return False


def article_status(article):
    if article.deleted:
        return "deleted"

    if article.draft:
        return "draft"

    return "published"


async def check_article_urls():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        articles = await session.scalars(
            select(Article)
            .options(selectinload(Article.author))
            .order_by(Article.created)
        )

        checked = 0
        found = 0

        for article in articles.unique():
            checked += 1

            for node_type, url in find_urls(article.document or []):
                if is_valid_url(node_type, url):
                    continue

                found += 1

                print(
                    f"[{article_status(article)}] {article.slug} "
                    f"by {article.author.username}: {node_type} {url!r}"
                )

        print(f"Checked {checked} articles, found {found} invalid urls")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(check_article_urls())
