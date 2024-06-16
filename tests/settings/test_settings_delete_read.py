from client_requests import request_settings_delete_read
from app.models import MangaRead, NovelRead, Log
from client_requests import request_read_add
from sqlalchemy import select, desc, func
from app import constants


async def test_settings_delete_read(
    client,
    aggregator_manga,
    aggregator_manga_info,
    aggregator_novel,
    aggregator_novel_info,
    create_dummy_user,
    create_test_user,
    get_dummy_token,
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
    # Add manga to read list
    await request_read_add(
        client,
        "manga",
        "berserk-fb9fbd",
        get_dummy_token,
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
        get_dummy_token,
        {
            "status": "completed",
            "note": "Test novel",
            "volumes": 20,
            "chapters": 60,
            "score": 9,
        },
    )

    # Check test user entries in database
    manga_read_count_test = await test_session.scalar(
        select(func.count(MangaRead.id)).filter(
            MangaRead.user == create_test_user
        )
    )

    novel_read_count_test = await test_session.scalar(
        select(func.count(NovelRead.id)).filter(
            NovelRead.user == create_test_user
        )
    )

    assert manga_read_count_test == 1
    assert novel_read_count_test == 1

    # Check dummy user entries in database
    manga_read_count_dummy = await test_session.scalar(
        select(func.count(MangaRead.id)).filter(
            MangaRead.user == create_dummy_user
        )
    )

    novel_read_count_dummy = await test_session.scalar(
        select(func.count(NovelRead.id)).filter(
            NovelRead.user == create_dummy_user
        )
    )

    assert manga_read_count_dummy == 1
    assert novel_read_count_dummy == 1

    # Request manga read list deletion for test user
    await request_settings_delete_read(client, "manga", get_test_token)

    # Check test user entries in database
    manga_read_count_test = await test_session.scalar(
        select(func.count(MangaRead.id)).filter(
            MangaRead.user == create_test_user
        )
    )

    novel_read_count_test = await test_session.scalar(
        select(func.count(NovelRead.id)).filter(
            NovelRead.user == create_test_user
        )
    )

    assert manga_read_count_test == 0
    assert novel_read_count_test == 1

    # Request novel read list deletion for test user
    await request_settings_delete_read(client, "novel", get_test_token)

    # Check test user entries in database
    manga_read_count_test = await test_session.scalar(
        select(func.count(MangaRead.id)).filter(
            MangaRead.user == create_test_user
        )
    )

    novel_read_count_test = await test_session.scalar(
        select(func.count(NovelRead.id)).filter(
            NovelRead.user == create_test_user
        )
    )

    assert manga_read_count_test == 0
    assert novel_read_count_test == 0

    # Check dummy user entries in database
    manga_read_count_dummy = await test_session.scalar(
        select(func.count(MangaRead.id)).filter(
            MangaRead.user == create_dummy_user
        )
    )

    novel_read_count_dummy = await test_session.scalar(
        select(func.count(NovelRead.id)).filter(
            NovelRead.user == create_dummy_user
        )
    )

    assert manga_read_count_dummy == 1
    assert novel_read_count_dummy == 1

    # Check log
    logs = await test_session.scalars(
        select(Log)
        .filter(Log.log_type == constants.LOG_SETTINGS_READ_DELETE)
        .order_by(desc(Log.created))
    )

    for index, log in enumerate(logs):
        assert log.log_type == constants.LOG_SETTINGS_READ_DELETE
        assert log.user == create_test_user

        if index == 0:
            assert log.data["content_type"] == "novel"
            assert log.data["read_count"] == 1

        if index == 1:
            assert log.data["content_type"] == "manga"
            assert log.data["read_count"] == 1
