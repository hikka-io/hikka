from app.sync.search.anime import anime_document_ids_delete
from app.sync.search.anime import anime_documents
from app.sync.search import service
from sqlalchemy import select, func
from app.models import Anime


class FakeIndex:
    uid = "anime"

    def __init__(self):
        self.batches = []
        self.deleted = []

    async def add_documents(self, documents, primary_key=None):
        self.batches.append(documents)

    async def delete_documents(self, ids):
        self.deleted.extend(ids)


async def test_search_anime_sync(test_session, aggregator_anime):
    index = FakeIndex()

    await service.index_documents(
        test_session, index, anime_documents, primary_key="id", limit=5
    )

    # Imported anime are sent in batches paged by content id
    assert [len(batch) for batch in index.batches] == [5, 5, 5, 2]

    ids = [document["id"] for batch in index.batches for document in batch]
    assert len(set(ids)) == 17
    assert ids == sorted(ids)

    flagged = await test_session.scalar(
        select(func.count(Anime.id)).filter(
            Anime.needs_search_update == True  # noqa: E712
        )
    )

    assert flagged == 0

    # Deleted anime is removed from the index
    anime = await test_session.scalar(
        select(Anime).filter(
            Anime.slug == "fullmetal-alchemist-brotherhood-fc524a"
        )
    )

    anime.needs_search_update = True
    anime.deleted = True
    test_session.add(anime)
    await test_session.commit()

    await service.delete_documents(
        test_session, index, anime_document_ids_delete
    )

    await test_session.refresh(anime)

    assert index.deleted == [anime.content_id]
    assert anime.needs_search_update is False
