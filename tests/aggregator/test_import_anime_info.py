from sqlalchemy.orm import selectinload
from app.models import Anime, Edit
from sqlalchemy import select
from app import constants


async def test_import_anime_info(
    test_session,
    aggregator_genres,
    aggregator_anime,
    aggregator_people,
    aggregator_characters,
    aggregator_anime_roles,
    aggregator_anime_info,
):
    # Check individual anime
    anime = await test_session.scalar(
        select(Anime)
        .filter(Anime.slug == "fullmetal-alchemist-brotherhood-fc524a")
        .options(selectinload(Anime.genres))
        .options(selectinload(Anime.episodes_list))
        .options(selectinload(Anime.voices))
        .options(selectinload(Anime.staff))
    )

    assert anime is not None
    assert anime.synopsis_ua is not None
    assert anime.needs_search_update is True
    assert anime.needs_update is False
    assert anime.image is not None

    assert len(anime.genres) == 5
    assert len(anime.episodes_list) == 64
    assert len(anime.voices) == 191
    assert len(anime.staff) == 78
    assert len(anime.external) == 11

    assert anime.external[0]["type"] == constants.EXTERNAL_GENERAL
    assert anime.external[0]["text"] == "Official Site"

    assert anime.external[-1]["type"] == constants.EXTERNAL_WATCH
    assert anime.external[-1]["text"] == "Toloka"

    # Check edit
    edit = await test_session.scalar(select(Edit).filter(Edit.edit_id == 1))

    assert edit.content.slug == "fullmetal-alchemist-brotherhood-fc524a"
    assert edit.status == constants.EDIT_ACCEPTED
    assert edit.system_edit is True

    # I'm not particullarly fan of this approach but this will do for now
    assert edit.before == {
        "translated_ua": False,
        "duration": None,
        "external": [],
        "ost": [],
        "rating": None,
        "source": None,
        "synonyms": [],
        "synopsis_en": None,
        "synopsis_ua": None,
        "videos": [],
        "schedule": [],
    }

    assert edit.after == {
        "translated_ua": True,
        "duration": 24,
        "external": [
            {
                "text": "Official Site",
                "type": "general",
                "url": "http://www.hagaren.jp/fa/",
            },
            {
                "text": "@hagaren_anime",
                "type": "general",
                "url": "https://twitter.com/hagaren_anime",
            },
            {
                "text": "AniDB",
                "type": "general",
                "url": "https://anidb.net/perl-bin/animedb.pl?show=anime&aid=6107",
            },
            {
                "text": "ANN",
                "type": "general",
                "url": "https://www.animenewsnetwork.com/encyclopedia/anime.php?id=10216",
            },
            {
                "text": "Wikipedia",
                "type": "general",
                "url": "https://en.wikipedia.org/wiki/Fullmetal_Alchemist:_Brotherhood",
            },
            {
                "text": "Wikipedia",
                "type": "general",
                "url": "https://ja.wikipedia.org/wiki/%E9%8B%BC%E3%81%AE%E9%8C%AC%E9%87%91%E8%A1%93%E5%B8%AB_FULLMETAL_ALCHEMIST",
            },
            {
                "text": "Syoboi",
                "type": "general",
                "url": "https://cal.syoboi.jp/tid/1575",
            },
            {
                "text": "Crunchyroll",
                "type": "general",
                "url": "http://www.crunchyroll.com/series-271031",
            },
            {
                "text": "Funimation",
                "type": "general",
                "url": "https://www.funimation.com/shows/fullmetal-alchemist-brotherhood",
            },
            {
                "text": "Anitube",
                "type": "watch",
                "url": "https://anitube.in.ua/48-staleviy-alhmk-braterstvo.html",
            },
            {
                "text": "Toloka",
                "type": "watch",
                "url": "http://toloka.to/t23388",
            },
        ],
        "ost": [
            {
                "author": "YUI",
                "index": 1,
                "ost_type": "opening",
                "spotify": "https://open.spotify.com/track/4OQq1bcP12GQQXJNupxqfR",
                "title": "again",
            },
            {
                "author": "NICO",
                "index": 2,
                "ost_type": "opening",
                "spotify": "https://open.spotify.com/track/3s067jTdOv8wnuUHeXdtjT",
                "title": "Hologram (ホログラム)",
            },
            {
                "author": "Sukima",
                "index": 3,
                "ost_type": "opening",
                "spotify": "https://open.spotify.com/track/66DAA9F0AFPpDvezYunqm3",
                "title": "Golden Time Lover (ゴールデンタイムラバー)",
            },
            {
                "author": "Chemistry",
                "index": 4,
                "ost_type": "opening",
                "spotify": "https://open.spotify.com/track/2Hv8CIxNzaCJoRPEzdvMTY",
                "title": "Period",
            },
            {
                "author": "SID",
                "index": 5,
                "ost_type": "opening",
                "spotify": "https://open.spotify.com/track/2LZ9iobmtiQa52mZMIebuH",
                "title": "Rain (レイン)",
            },
            {
                "author": "SID",
                "index": 1,
                "ost_type": "ending",
                "spotify": "https://open.spotify.com/track/0ODOmKxO0CKv4DzoP3HHIC",
                "title": "Uso (嘘)",
            },
            {
                "author": "Miho",
                "index": 2,
                "ost_type": "ending",
                "spotify": "https://open.spotify.com/track/3O6uWEmwDlkT7EmucuRdvB",
                "title": "LET IT OUT",
            },
            {
                "author": "Lil'B",
                "index": 3,
                "ost_type": "ending",
                "spotify": "https://open.spotify.com/track/7934ie1UyuInkuzQimJjjn",
                "title": "Tsunaida Te (つないだ手)",
            },
            {
                "author": "SCANDAL",
                "index": 4,
                "ost_type": "ending",
                "spotify": "https://open.spotify.com/track/2CFY24ovop3Ueel7ECzw0Y",
                "title": "Shunkan Sentimental (瞬間センチメンタル)",
            },
            {
                "author": "Nakagawa",
                "index": 5,
                "ost_type": "ending",
                "spotify": "https://open.spotify.com/track/18dGnO3Gc6dGTgLoQLwsVN",
                "title": "RAY OF LIGHT",
            },
            {
                "author": "SID",
                "index": 6,
                "ost_type": "ending",
                "spotify": "https://open.spotify.com/track/2LZ9iobmtiQa52mZMIebuH",
                "title": "Rain (レイン)",
            },
            {
                "author": "NICO",
                "index": 7,
                "ost_type": "ending",
                "spotify": "https://open.spotify.com/track/3s067jTdOv8wnuUHeXdtjT",
                "title": "Hologram (ホログラム)",
            },
        ],
        "rating": "r",
        "source": "manga",
        "synonyms": [
            "Hagane no Renkinjutsushi: Fullmetal Alchemist",
            "Fullmetal Alchemist (2009)",
            "FMA",
            "FMAB",
        ],
        "synopsis_en": "After a horrific alchemy experiment goes wrong in the Elric "
        "household, brothers Edward and Alphonse are left in a "
        "catastrophic new reality. Ignoring the alchemical principle "
        "banning human transmutation, the boys attempted to bring "
        "their recently deceased mother back to life. Instead, they "
        "suffered brutal personal loss: Alphonse's body disintegrated "
        "while Edward lost a leg and then sacrificed an arm to keep "
        "Alphonse's soul in the physical realm by binding it to a "
        "hulking suit of armor.\n"
        "\n"
        "The brothers are rescued by their neighbor Pinako Rockbell "
        "and her granddaughter Winry. Known as a bio-mechanical "
        "engineering prodigy, Winry creates prosthetic limbs for "
        'Edward by utilizing "automail," a tough, versatile metal used '
        "in robots and combat armor. After years of training, the "
        "Elric brothers set off on a quest to restore their bodies by "
        "locating the Philosopher's Stone—a powerful gem that allows "
        "an alchemist to defy the traditional laws of Equivalent "
        "Exchange.\n"
        "\n"
        "As Edward becomes an infamous alchemist and gains the "
        'nickname "Fullmetal," the boys\' journey embroils them in a '
        "growing conspiracy that threatens the fate of the world.\n"
        "\n"
        "[Written by MAL Rewrite]",
        "synopsis_ua": "Порушивши головну заборону Алхімії і спробувавши воскресити "
        "маму, талановиті брати Елріки заплатили високу ціну: "
        "молодший, Альфонс, втратив тіло, і тепер його душа "
        "прикріплена до сталевих обладунків, а старший, Едвард, "
        "позбувся руки і ноги, тому йому доводиться користуватися "
        "протезами - автобронею. Завдяки виявленим здібностям Ед "
        "отримав звання державного алхіміка і, таким чином, став "
        "частиною військової машини держави. Тепер у нього є шанс "
        "повернути Алу колишнє тіло. Попереду мандри і пригоди, "
        "розгадки страшних таємниць і нескінченні битви...У порівнянні "
        "з першою екранізацією, в оновленому «Сталевому алхіміку» "
        "дизайн персонажів став більш «дорослим». У цілому це більш "
        "динамічний твір. З першої ж серії героїв кидає у вир подій: "
        "різанина в Іштварі, боротьба відступників з Армією і фюрером "
        "Бредлі, гомункули і численні «натяки» на подальший розвиток "
        "історії.\n"
        "\n"
        "Джерело: Anitube",
        "videos": [
            {
                "description": '"again" by YUI',
                "title": "OP 1 (Artist ver.)",
                "url": "https://youtu.be/Xlryitu2Jo0",
                "video_type": "video_music",
            },
            {
                "description": None,
                "title": "OP 1 (Artist ver.)",
                "url": "https://youtu.be/EpPzg3_276o",
                "video_type": "video_music",
            },
            {
                "description": '"Hologram (ホログラム)" by NICO Touches the Walls',
                "title": "OP 2 (Artist ver.)",
                "url": "https://youtu.be/TbResk1x4kY",
                "video_type": "video_music",
            },
            {
                "description": '"Golden Time Lover (ゴールデンタイムラバー)" by Sukima '
                "Switch",
                "title": "OP 3 (Artist ver.)",
                "url": "https://youtu.be/0iAF8TJAqp4",
                "video_type": "video_music",
            },
            {
                "description": '"Period" by Chemistry',
                "title": "OP 4 (Artist ver.)",
                "url": "https://youtu.be/TCBi6YFTi7c",
                "video_type": "video_music",
            },
            {
                "description": '"Uso (嘘)" by SID',
                "title": "ED 1 (Artist ver.)",
                "url": "https://youtu.be/caV3V98_8AY",
                "video_type": "video_music",
            },
            {
                "description": '"LET IT OUT" by Miho Fukuhara',
                "title": "ED 2 (Artist ver.)",
                "url": "https://youtu.be/OJAbEWDTmBs",
                "video_type": "video_music",
            },
            {
                "description": '"Shunkan Sentimental (瞬間センチメンタル)" by SCANDAL',
                "title": "ED 4 (Artist ver.)",
                "url": "https://youtu.be/38bhs0MnvxI",
                "video_type": "video_music",
            },
            {
                "description": '"RAY OF LIGHT" by Nakagawa Shouko',
                "title": "ED 5 (Artist ver.)",
                "url": "https://youtu.be/EbTJugG46iA",
                "video_type": "video_music",
            },
            {
                "description": None,
                "title": "Announcement",
                "url": "https://youtu.be/--IcmZkvL0Q",
                "video_type": "video_promo",
            },
        ],
        "schedule": [
            {"episode": 5, "airing_at": 1696600800},
            {"episode": 6, "airing_at": 1697205600},
            {"episode": 7, "airing_at": 1697810400},
            {"episode": 8, "airing_at": 1698415200},
            {"episode": 9, "airing_at": 1699020000},
            {"episode": 10, "airing_at": 1699624800},
            {"episode": 11, "airing_at": 1700229600},
            {"episode": 12, "airing_at": 1700834400},
            {"episode": 13, "airing_at": 1701439200},
            {"episode": 14, "airing_at": 1702044000},
            {"episode": 15, "airing_at": 1702648800},
            {"episode": 16, "airing_at": 1703253600},
            {"episode": 17, "airing_at": 1704463200},
            {"episode": 18, "airing_at": 1705068000},
            {"episode": 19, "airing_at": 1705672800},
            {"episode": 20, "airing_at": 1706277600},
            {"episode": 21, "airing_at": 1706882400},
            {"episode": 22, "airing_at": 1707487200},
            {"episode": 23, "airing_at": 1708092000},
            {"episode": 24, "airing_at": 1708696800},
            {"episode": 25, "airing_at": 1709301600},
            {"episode": 26, "airing_at": 1709906400},
            {"episode": 27, "airing_at": 1710511200},
            {"episode": 28, "airing_at": 1711116000},
        ],
    }
