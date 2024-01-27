from app.comments import utils


async def test_empty_markdown():
    assert utils.is_empty_markdown("**text**") is False
    assert utils.is_empty_markdown("****") is True

    assert utils.is_empty_markdown("*text*") is False
    assert utils.is_empty_markdown("**") is True

    assert utils.is_empty_markdown("__text__") is False
    assert utils.is_empty_markdown("____") is True

    assert utils.is_empty_markdown("[Hikka](https://hikka.io)") is False
    assert utils.is_empty_markdown("[Hikka]()") is True

    assert utils.is_empty_markdown(":::spoiler text :::") is False
    assert utils.is_empty_markdown(":::spoiler  :::") is True

    assert utils.is_empty_markdown("__**text**__") is False
    assert utils.is_empty_markdown("***text***") is False

    assert utils.is_empty_markdown(":::spoiler        ::: **** ____") is True

    assert (
        utils.is_empty_markdown("** **** ____ [empty]() :::spoiler  :::")
        is True
    )
