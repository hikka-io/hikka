from app.aggregator.franchises import build_relations


# Content type, content id and MAL id
ANIME_A = ("anime", "a", 20)
ANIME_B = ("anime", "b", 10)
MANGA = ("manga", "m", 30)


def edge(source, target, relation_type):
    return {
        "relation_type": relation_type,
        "related_content_type": target[0],
        "related_content_id": target[1],
        "related_content": target[2],
        "content_type": source[0],
        "content_id": source[1],
        "content": source[2],
    }


def relation(source, target, relation_type):
    return {
        "relation_type": relation_type,
        "related_content_type": target[0],
        "related_content_id": target[1],
        "content_type": source[0],
        "content_id": source[1],
    }


async def test_relations_inverse():
    # Both sides agree so we store pair once in forward form
    assert build_relations(
        [
            edge(ANIME_A, ANIME_B, "sequel"),
            edge(ANIME_B, ANIME_A, "prequel"),
        ]
    ) == [relation(ANIME_A, ANIME_B, "sequel")]

    # Inverse relation from only one side is flipped
    assert build_relations([edge(ANIME_B, ANIME_A, "prequel")]) == [
        relation(ANIME_A, ANIME_B, "sequel")
    ]

    assert build_relations([edge(ANIME_B, ANIME_A, "full_story")]) == [
        relation(ANIME_A, ANIME_B, "summary")
    ]


async def test_relations_parent_story():
    # Parent story alone becomes side story
    assert build_relations([edge(ANIME_B, ANIME_A, "parent_story")]) == [
        relation(ANIME_A, ANIME_B, "side_story")
    ]

    # Exact type comes from the other side
    for relation_type in ["spin_off", "summary", "sequel"]:
        assert build_relations(
            [
                edge(ANIME_B, ANIME_A, "parent_story"),
                edge(ANIME_A, ANIME_B, relation_type),
            ]
        ) == [relation(ANIME_A, ANIME_B, relation_type)]

    # But symmetric relation from the other side loses to it
    assert build_relations(
        [
            edge(ANIME_B, ANIME_A, "parent_story"),
            edge(ANIME_A, ANIME_B, "alternative_version"),
        ]
    ) == [relation(ANIME_A, ANIME_B, "side_story")]


async def test_relations_priority():
    # Same direction, sequel beats side story
    assert build_relations(
        [
            edge(ANIME_A, ANIME_B, "prequel"),
            edge(ANIME_B, ANIME_A, "side_story"),
        ]
    ) == [relation(ANIME_B, ANIME_A, "sequel")]

    # Opposite directions, winner keeps its direction
    assert build_relations(
        [
            edge(ANIME_A, ANIME_B, "sequel"),
            edge(ANIME_B, ANIME_A, "side_story"),
        ]
    ) == [relation(ANIME_A, ANIME_B, "sequel")]

    # Summary beats side story
    assert build_relations(
        [
            edge(ANIME_A, ANIME_B, "full_story"),
            edge(ANIME_B, ANIME_A, "side_story"),
        ]
    ) == [relation(ANIME_B, ANIME_A, "summary")]

    # Same side listing other title twice uses better relation
    assert build_relations(
        [
            edge(ANIME_A, ANIME_B, "adaptation"),
            edge(ANIME_A, ANIME_B, "sequel"),
        ]
    ) == [relation(ANIME_A, ANIME_B, "sequel")]


async def test_relations_direction_by_mal_id():
    # Both sides say other one is spin-off so lower MAL id is source
    for edges in [
        [
            edge(ANIME_A, ANIME_B, "spin_off"),
            edge(ANIME_B, ANIME_A, "spin_off"),
        ],
        [
            edge(ANIME_B, ANIME_A, "spin_off"),
            edge(ANIME_A, ANIME_B, "spin_off"),
        ],
    ]:
        assert build_relations(edges) == [
            relation(ANIME_B, ANIME_A, "spin_off")
        ]


async def test_relations_symmetric():
    # Symmetric relations are stored once with lower MAL id as source
    assert build_relations(
        [
            edge(MANGA, ANIME_A, "adaptation"),
            edge(ANIME_A, MANGA, "adaptation"),
        ]
    ) == [relation(ANIME_A, MANGA, "adaptation")]

    # Anime and manga MAL ids may match, then content type decides
    manga = ("manga", "m", ANIME_A[2])

    assert build_relations([edge(manga, ANIME_A, "alternative_version")]) == [
        relation(ANIME_A, manga, "alternative_version")
    ]


async def test_relations_ignored():
    assert (
        build_relations(
            [
                edge(ANIME_A, ANIME_B, "other"),
                edge(ANIME_A, ANIME_B, "character"),
                edge(ANIME_A, ANIME_B, "unknown"),
                edge(ANIME_A, ANIME_A, "sequel"),
            ]
        )
        == []
    )
