from app.database import sessionmanager
from app.service import create_log
from app.utils import get_settings
from app.models import Article
from sqlalchemy import select
from app import constants
import asyncio


def remove_preview(article_document):
    def _process_document(document):
        result = []

        for node in document:
            if "children" in node:
                node["children"] = _process_document(node["children"])

                if node["type"] == "preview":
                    result.extend(node["children"])
                    continue

            result.append(node)

        return result

    return _process_document(article_document)


async def fix_remove_preview():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        articles = await session.scalars(
            select(Article).order_by(Article.created.desc())
        )

        for article in articles.unique():
            before_document = article.document
            article.document = remove_preview(article.document)
            after_document = article.document

            if before_document != after_document:
                await create_log(
                    session,
                    constants.LOG_ARTICLE_UPDATE,
                    None,
                    article.id,
                    {
                        "before": {"document": before_document},
                        "after": {"document": after_document},
                    },
                )

                print(f"Removed preview from {article.title}")

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_remove_preview())
