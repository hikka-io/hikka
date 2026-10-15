from meilisearch_python_sdk.models.settings import MeilisearchSettings
from app.utils import get_settings, to_timestamp
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.database import sessionmanager
from sqlalchemy import select
from app.models import User
from app import constants
from uuid import UUID


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


async def user_documents(
    session: AsyncSession, limit: int, last_id: UUID | None
):
    query = (
        select(User)
        .filter(User.needs_search_update == True)  # noqa: E712
        .order_by(User.id)
        .limit(limit)
    )

    # Rows drop out of the filter once indexed so we page by key
    if last_id:
        query = query.filter(User.id > last_id)

    users_list = await session.scalars(query)

    documents = []

    for user in users_list:
        documents.append(user_to_document(user))
        last_id = user.id

        # I'm not sure if this would behave correctly if Meilisearch is down
        user.needs_search_update = False
        session.add(user)

    return documents, last_id


async def meilisearch_populate(session: AsyncSession):
    # print("Meilisearch: Populating users")

    settings = get_settings()

    async with AsyncClient(**settings.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_USERS)

        await update_user_settings(index)

        size = 1000
        last_id = None

        while True:
            documents, last_id = await user_documents(session, size, last_id)

            if len(documents) == 0:
                break

            await index.add_documents(documents)

            # Let's just hope if Meilisearch is down this fails ;)
            await session.commit()


async def update_search_users():
    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
