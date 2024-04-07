from meilisearch_python_sdk.models.settings import MeilisearchSettings
from app.utils import get_settings, to_timestamp
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from sqlalchemy import select, asc, func
from app.database import sessionmanager
from app.utils import pagination
from app.models import User
from app import constants
import math


async def update_user_settings(index):
    await index.update_settings(
        MeilisearchSettings(
            searchable_attributes=["username"],
            filterable_attributes=["created"],
            displayed_attributes=["username"],
            sortable_attributes=["created"],
            distinct_attribute="username",
        )
    )


def user_to_document(user: User):
    return {
        "created": to_timestamp(user.created),
        "username": user.username,
        "id": user.reference,
    }


async def user_documents(session: AsyncSession, limit: int, offset: int):
    users_list = await session.scalars(
        select(User)
        .filter(User.needs_search_update == True)  # noqa: E712
        .order_by(asc(User.created))
        .limit(limit)
        .offset(offset)
    )

    documents = []

    for user in users_list:
        documents.append(user_to_document(user))

        # I'm not sure if this would behave correctly if Meilisearch is down
        user.needs_search_update = False
        session.add(user)

    return documents


async def user_documents_total(session: AsyncSession):
    return await session.scalar(
        select(func.count(User.id)).filter(
            User.needs_search_update == True,  # noqa: E712
        )
    )


async def meilisearch_populate(session: AsyncSession):
    # print("Meilisearch: Populating users")

    settings = get_settings()

    async with AsyncClient(**settings.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_USERS)

        await update_user_settings(index)

        size = 1000
        total = await user_documents_total(session)
        pages = math.ceil(total / size)

        for page in range(1, pages + 1):
            # print(f"Meilisearch: Processing users page {page} of {pages}")

            limit, offset = pagination(page, size)
            documents = await user_documents(session, limit, offset)

            await index.add_documents(documents)

            # Let's just hope if Meilisearch is down this fails ;)
            await session.commit()


async def update_search_users():
    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
