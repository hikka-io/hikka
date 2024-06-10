from app.models import Novel, NovelEdit
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from app import constants


async def test_import_novel_info(
    test_session,
    aggregator_genres,
    aggregator_novel,
    aggregator_people,
    aggregator_characters,
    aggregator_manga_roles,
    aggregator_novel_info,
):
    # Check individual novel
    novel = await test_session.scalar(
        select(Novel)
        .filter(Novel.slug == "kono-subarashii-sekai-ni-shukufuku-wo-cc5525")
        .options(joinedload(Novel.authors))
        .options(joinedload(Novel.genres))
    )

    assert novel is not None
    assert novel.synopsis_en is not None
    assert novel.needs_search_update is True
    assert novel.needs_update is False

    assert len(novel.genres) == 5
    # assert len(novel.authors) == 1
    assert len(novel.external) == 3
    assert novel.chapters == 127
    assert novel.volumes == 17

    assert novel.external[0]["type"] == constants.EXTERNAL_GENERAL
    assert novel.external[0]["text"] == "Official Site"

    # Check edit
    edit = await test_session.scalar(
        select(NovelEdit)
        .filter(NovelEdit.edit_id == 2)
        .options(joinedload(NovelEdit.content))
    )

    assert edit.content.slug == "kono-subarashii-sekai-ni-shukufuku-wo-cc5525"
    assert edit.content_type == constants.CONTENT_NOVEL
    assert edit.status == constants.EDIT_ACCEPTED
    assert edit.system_edit is True

    # I'm not particullarly fan of this approach but this will do for now
    assert edit.before == {
        "external": [],
        "synopsis_en": None,
    }

    assert edit.after == {
        "external": [
            {
                "url": "http://www.sneakerbunko.jp/series/konosuba/",
                "text": "Official Site",
                "type": "general",
            },
            {
                "url": "https://en.wikipedia.org/wiki/KonoSuba",
                "text": "Wikipedia",
                "type": "general",
            },
            {
                "url": "https://ja.wikipedia.org/wiki/%E3%81%93%E3%81%AE%E7%B4%A0%E6%99%B4%E3%82%89%E3%81%97%E3%81%84%E4%B8%96%E7%95%8C%E3%81%AB%E7%A5%9D%E7%A6%8F%E3%82%92!",
                "text": "Wikipedia",
                "type": "general",
            },
        ],
        "synopsis_en": "Kazuma Satou lives a laughable and pathetic life, "
        "being a shut-in NEET with no distinguishable qualities other than an "
        "addiction to video games. On his way home, Kazuma dies trying to "
        "save a girl from an oncoming truck—or so he believes. In reality, "
        'the "truck" was a slow-moving tractor, and he merely died from '
        "shock.\n\nWaking up in limbo between death and heaven, Kazuma "
        "finds himself facing the arrogant goddess Aqua. Here, he must choose "
        "between two options: go on to heaven or be sent to a fantasy world "
        "that needs his help to defeat the Demon King. Initially unimpressed "
        "by the challenging prospect of fighting a Demon King, Kazuma changes "
        "his mind after Aqua tells him he can bring any one item he wants. "
        "What better choice does Kazuma have than the goddess standing before "
        "him?\n\nUnfortunately, after the two arrive in their new world, "
        "two things become clear: Aqua is useless beyond belief, and life in "
        "this fantasy realm will be anything but smooth sailing. From paying "
        "for food and accommodations to trying to learn new skills, the "
        "duo's problems are just starting to take shape—and the arrival of "
        "eccentric allies may only make things "
        "worse.\n\n[Written by MAL Rewrite]",
    }
