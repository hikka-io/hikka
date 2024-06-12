from app.models import Manga, MangaEdit
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from app import constants


async def test_import_manga_info(
    test_session,
    aggregator_genres,
    aggregator_manga,
    aggregator_people,
    aggregator_characters,
    aggregator_manga_roles,
    aggregator_manga_info,
):
    # Check individual manga
    manga = await test_session.scalar(
        select(Manga)
        .filter(Manga.slug == "fullmetal-alchemist-7ef8d2")
        .options(joinedload(Manga.authors))
        .options(joinedload(Manga.genres))
    )

    assert manga is not None
    assert manga.synopsis_en is not None
    assert manga.needs_search_update is True
    assert manga.needs_update is False

    assert len(manga.genres) == 6
    assert len(manga.authors) == 1
    assert len(manga.external) == 3
    assert manga.chapters == 116
    assert manga.volumes == 27

    assert manga.external[0]["type"] == constants.EXTERNAL_GENERAL
    assert manga.external[0]["text"] == "Official Site"

    # Check edit
    edit = await test_session.scalar(
        select(MangaEdit)
        .filter(MangaEdit.edit_id == 2)
        .options(joinedload(MangaEdit.content))
    )

    assert edit.content.slug == "fullmetal-alchemist-7ef8d2"
    assert edit.content_type == constants.CONTENT_MANGA
    assert edit.status == constants.EDIT_ACCEPTED
    assert edit.system_edit is True

    # I'm not particullarly fan of this approach but this will do for now
    assert edit.before == {
        "external": [],
        "synonyms": [],
        "synopsis_en": None,
    }

    assert edit.after == {
        "external": [
            {
                "url": "http://gangan.square-enix.co.jp/hagaren/",
                "text": "Official Site",
                "type": "general",
            },
            {
                "url": "http://ja.wikipedia.org/wiki/%E9%8B%BC%E3%81%AE%E9%8C%AC%E9%87%91%E8%A1%93%E5%B8%AB",
                "text": "Wikipedia",
                "type": "general",
            },
            {
                "url": "https://en.wikipedia.org/wiki/Fullmetal_Alchemist",
                "text": "Wikipedia",
                "type": "general",
            },
        ],
        "synonyms": [
            "Full Metal Alchemist",
            " Hagane no Renkinjutsushi",
            " FMA",
            " HagaRen",
            " Fullmetal Alchemist Gaiden",
        ],
        "synopsis_en": "Alchemists are knowledgeable and naturally talented "
        "individuals who can manipulate and modify matter due to their art. "
        "Yet despite the wide range of possibilities, alchemy is not as "
        "all-powerful as most would believe. Human transmutation is strictly "
        "forbidden, and whoever attempts it risks severe consequences. Even "
        "so, siblings Edward and Alphonse Elric decide to ignore this great "
        "taboo and bring their mother back to life. Unfortunately, not only "
        "do they fail in resurrecting her, they also pay an extremely high "
        "price for their arrogance: Edward loses his left leg and Alphonse "
        "his entire body. Furthermore, Edward also gives up his right arm in "
        "order to seal his brother's soul into a suit of armor.\n\nYears "
        "later, the young alchemists travel across the country looking for "
        "the Philosopher's Stone, in the hopes of recovering their old "
        "bodies with its power. However, their quest for the fated stone "
        "also leads them to unravel far darker secrets than they could ever "
        "imagine.\n\n[Written by MAL Rewrite]",
    }
