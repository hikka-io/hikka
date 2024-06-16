from client_requests import request_settings_import_read
from client_requests import request_read_add
from sqlalchemy import select, desc, func
from fastapi import status
from app import constants

from app.models import (
    MangaRead,
    NovelRead,
    Novel,
    Log,
)


async def test_settings_import_read_overwrite(
    client,
    create_test_user,
    aggregator_manga,
    aggregator_novel,
    aggregator_manga_info,
    aggregator_novel_info,
    get_test_token,
    test_session,
):
    # Add manga to read list
    await request_read_add(
        client,
        "manga",
        "berserk-fb9fbd",
        get_test_token,
        {
            "status": "reading",
            "note": "Test manga",
            "volumes": 1,
            "chapters": 1,
            "score": 7,
        },
    )

    # Add novel to read list
    await request_read_add(
        client,
        "novel",
        "kono-subarashii-sekai-ni-shukufuku-wo-cc5525",
        get_test_token,
        {
            "status": "completed",
            "note": "Test novel",
            "volumes": 20,
            "chapters": 60,
            "score": 9,
        },
    )

    # Create import request
    response = await request_settings_import_read(
        client,
        get_test_token,
        {
            "overwrite": True,
            "content": [
                {
                    "my_times_read": 1,
                    "manga_mangadb_id": 60553,  # Konosuba (novel)
                    "my_read_chapters": 1,
                    "my_read_volumes": 1,
                    "my_score": 10,
                    "my_status": "Reading",
                    "my_comments": "Nice novel",
                },
                {
                    "my_times_read": 0,
                    "manga_mangadb_id": 130826,  # Tian (novel)
                    "my_read_chapters": 2,
                    "my_read_volumes": 3,
                    "my_score": 7,
                    "my_status": "Reading",
                    "my_comments": {},
                },
                {
                    "my_times_read": 0,
                    "manga_mangadb_id": 125036,  # Horizon (manga)
                    "my_read_chapters": 0,
                    "my_read_volumes": 0,
                    "my_score": 0,
                    "my_status": "Plan to Read",
                    "my_comments": {},
                },
            ],
        },
    )

    # Check status
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True

    # Check entries in database
    manga_read_count = await test_session.scalar(
        select(func.count(MangaRead.id)).filter(
            MangaRead.user == create_test_user
        )
    )

    novel_read_count = await test_session.scalar(
        select(func.count(NovelRead.id)).filter(
            NovelRead.user == create_test_user
        )
    )

    assert manga_read_count == 2
    assert novel_read_count == 2

    # Get Konosuba novel entry
    novel_konosuba = await test_session.scalar(
        select(Novel).filter(
            Novel.slug == "kono-subarashii-sekai-ni-shukufuku-wo-cc5525"
        )
    )

    # Watch entry shouldn't be changed after import
    read = await test_session.scalar(
        select(NovelRead).filter(
            NovelRead.content == novel_konosuba,
            NovelRead.user == create_test_user,
        )
    )

    assert read is not None
    assert read.status == constants.READ_READING
    assert read.chapters == 1
    assert read.rereads == 1
    assert read.volumes == 1
    assert read.score == 10

    # Check log
    log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    assert log.log_type == constants.LOG_SETTINGS_IMPORT_READ
    assert log.data["imported_novel"] == 2
    assert log.data["imported_manga"] == 1
    assert log.data["overwrite"] is True
    assert log.user == create_test_user
