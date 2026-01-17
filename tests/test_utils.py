from datetime import datetime
from app import constants
from app import utils


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
    assert utils.is_empty_markdown(":::spoiler:::") is True

    assert utils.is_empty_markdown("__**text**__") is False
    assert utils.is_empty_markdown("***text***") is False

    assert utils.is_empty_markdown(":::spoiler        ::: **** ____") is True

    assert (
        utils.is_empty_markdown("** **** ____ [empty]() :::spoiler  :::")
        is True
    )


def test_token():
    assert len(utils.new_token()) == 43


def test_password():
    password = "password"
    password_hash = utils.hashpwd(password)

    assert len(password_hash) == 60
    assert utils.checkpwd(password, password_hash) is True
    assert utils.checkpwd("bad_password", password_hash) is False


def test_slugify():
    # Simple test for slug creation
    assert (
        utils.slugify("Kono Subarashii Sekai ni Shukufuku wo!")
        == "kono-subarashii-sekai-ni-shukufuku-wo"
    )

    # Test for Ukrainian transliteration
    assert (
        utils.slugify("Цей прекрасний світ, благословенний Богом!")
        == "tsey-prekrasnyy-svit-blahoslovennyy-bohom"
    )

    # Test for content id suffix
    assert (
        utils.slugify(
            "Kono Subarashii Sekai ni Shukufuku wo!",
            content_id="04d0ce79-9d96-49fb-8ab5-005d9ff100df",
        )
        == "kono-subarashii-sekai-ni-shukufuku-wo-04d0ce"
    )

    # Test for max length
    assert (
        utils.slugify(
            "Цей прекрасний світ, благословенний Богом!",
            max_length=20,
        )
        == "tsey-prekrasnyy-svit"
    )

    # Now let's make sure everything works in together
    assert (
        utils.slugify(
            "Kono Subarashii Sekai ni Shukufuku wo!",
            content_id="04d0ce79-9d96-49fb-8ab5-005d9ff100df",
            max_length=21,
        )
        == "kono-subarashii-sekai-04d0ce"
    )

    # Empty slug should generate random 22 characters (16 bytes) string
    assert len(utils.slugify("")) == 22


def test_chunkify():
    chunks = utils.chunkify([1, 2, 3, 4, 5, 6, 7, 8, 9], 3)

    assert len(chunks) == 3

    assert chunks[0] == [1, 2, 3]
    assert chunks[1] == [4, 5, 6]
    assert chunks[2] == [7, 8, 9]


def test_season():
    assert utils.get_season(datetime(2023, 1, 1)) == constants.SEASON_WINTER
    assert utils.get_season(datetime(2023, 4, 1)) == constants.SEASON_SPRING
    assert utils.get_season(datetime(2023, 7, 1)) == constants.SEASON_SUMMER
    assert utils.get_season(datetime(2023, 10, 1)) == constants.SEASON_FALL


def test_timestamp():
    assert utils.from_timestamp(1693168107) == datetime(2023, 8, 27, 20, 28, 27)
    assert utils.to_timestamp(datetime(2023, 8, 27, 20, 28, 27)) == 1693168107


def test_pagination():
    page = 3
    total = 50

    limit, offset = utils.pagination(page, constants.SEARCH_RESULT_SIZE)

    assert limit == 15
    assert offset == 30

    assert {
        "page": 3,
        "pages": 4,
        "total": 50,
    } == utils.pagination_dict(
        total,
        page,
        limit,
    )
