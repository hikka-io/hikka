from sqlalchemy.ext.asyncio import AsyncSession


async def get_documents(
    session: AsyncSession, query, key, to_document, limit: int, last_id
):
    # Rows stay locked until the batch is committed so edits made
    # meanwhile wait and flag the row again instead of being overwritten
    query = (
        query.order_by(key)
        .limit(limit)
        .with_for_update(of=key.class_, skip_locked=True)
    )

    # Rows drop out of the filter once indexed so we page by key
    if last_id:
        query = query.filter(key > last_id)

    rows = await session.scalars(query)

    documents = []

    for row in rows.unique():
        documents.append(to_document(row))
        last_id = getattr(row, key.key)

        row.needs_search_update = False
        session.add(row)

    return documents, last_id


async def get_delete_ids(session: AsyncSession, query, key):
    rows = await session.scalars(
        query.with_for_update(of=key.class_, skip_locked=True)
    )

    delete_ids = []

    for row in rows.unique():
        # Document ids are strings and articles use their UUID
        delete_ids.append(str(getattr(row, key.key)))

        row.needs_search_update = False
        session.add(row)

    return delete_ids


async def index_documents(
    session: AsyncSession,
    index,
    get_batch,
    primary_key: str | None = None,
    limit: int = 1000,
):
    last_id = None

    while True:
        documents, last_id = await get_batch(session, limit, last_id)

        if len(documents) == 0:
            break

        await index.add_documents(documents, primary_key=primary_key)

        # Commit each batch so row locks are released right away
        await session.commit()


async def delete_documents(session: AsyncSession, index, get_ids):
    delete_ids = await get_ids(session)

    if len(delete_ids) > 0:
        await index.delete_documents(delete_ids)
        print(f"Meilisearch: deleted {len(delete_ids)} from {index.uid}")

    # Flags are only cleared once documents are gone from the index
    await session.commit()
