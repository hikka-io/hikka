from sqlalchemy import select
from app import constants
from app import utils

from app.models import (
    Franchise,
    Anime,
    Manga,
    Novel,
)


# Inverse relations are flipped
INVERSE_RELATIONS = {
    constants.RELATION_PREQUEL: constants.RELATION_SEQUEL,
    constants.RELATION_FULL_STORY: constants.RELATION_SUMMARY,
    constants.RELATION_PARENT_STORY: None,
}

# These have no real direction so we store first to appear
SYMMETRIC_RELATIONS = [
    constants.RELATION_ALTERNATIVE_SETTING,
    constants.RELATION_ALTERNATIVE_VERSION,
    constants.RELATION_ADAPTATION,
]

# Relations ordered by priority
RELATIONS_PRIORITY = [
    constants.RELATION_SEQUEL,
    constants.RELATION_SUMMARY,
    constants.RELATION_SPIN_OFF,
    constants.RELATION_SIDE_STORY,
    constants.RELATION_ALTERNATIVE_SETTING,
    constants.RELATION_ALTERNATIVE_VERSION,
    constants.RELATION_ADAPTATION,
]


def relation_priority(claim):
    # Parent story without exact type counts as side story
    return RELATIONS_PRIORITY.index(claim[2] or constants.RELATION_SIDE_STORY)


def canonical_claim(entry):
    source = (entry["content_type"], entry["content_id"])
    target = (entry["related_content_type"], entry["related_content_id"])
    relation_type = entry["relation_type"]

    if relation_type in INVERSE_RELATIONS:
        return target, source, INVERSE_RELATIONS[relation_type]

    return source, target, relation_type


def is_directed(relation_type):
    if relation_type is None:
        return False

    return relation_type not in SYMMETRIC_RELATIONS


def merge_claims(claims, mal_ids):
    """Merge what both sides of a pair say about each other"""

    if len(claims) == 2 and claims[0][:2] == claims[1][:2]:
        first, second = claims

        # Parent story gives direction, other side gives exact type
        if first[2] is None and is_directed(second[2]):
            return second

        if second[2] is None and is_directed(first[2]):
            return first

    claims = [
        (source, target, relation_type or constants.RELATION_SIDE_STORY)
        for source, target, relation_type in claims
    ]

    best = min(claims, key=relation_priority)
    same_type = [claim for claim in claims if claim[2] == best[2]]

    # If we can't decide priority let older mal_id do that for us
    if best[2] in SYMMETRIC_RELATIONS or (
        len(same_type) == 2 and same_type[0][:2] != same_type[1][:2]
    ):
        source, target = sorted(
            best[:2], key=lambda node: (mal_ids[node], node)
        )

        best = (source, target, best[2])

    return best


def build_relations(entries):
    """Turn aggregator franchise edges into one relation per pair"""

    mal_ids = {}
    pairs = {}

    for entry in entries:
        # Let's not crash if aggregator has messed up
        if not entry.get("content_id") or not entry.get("related_content_id"):
            continue

        if (
            entry["relation_type"] not in INVERSE_RELATIONS
            and entry["relation_type"] not in RELATIONS_PRIORITY
        ):
            continue

        side = (entry["content_type"], entry["content_id"])
        related = (entry["related_content_type"], entry["related_content_id"])
        claim = canonical_claim(entry)

        mal_ids[side] = entry["content"]
        mal_ids[related] = entry["related_content"]

        if claim[0] == claim[1]:
            continue

        sides = pairs.setdefault(frozenset(claim[:2]), {})

        # Same side may list other title more than once
        if side not in sides or (
            relation_priority(claim) < relation_priority(sides[side])
        ):
            sides[side] = claim

    # Sorted so unchanged franchise always produces same value
    merged = sorted(
        merge_claims(list(sides.values()), mal_ids) for sides in pairs.values()
    )

    return [
        {
            "relation_type": relation_type,
            "related_content_type": target[0],
            "related_content_id": target[1],
            "content_type": source[0],
            "content_id": source[1],
        }
        for source, target, relation_type in merged
    ]


# TODO: optimize it
async def save_franchises_list(session, data):
    content_ids = [entry["content_id"] for entry in data]

    cache = await session.scalars(
        select(Franchise).filter(Franchise.content_id.in_(content_ids))
    )

    franchises_cache = {entry.content_id: entry for entry in cache}

    for franchise_data in data:
        if not (
            franchise := franchises_cache.get(franchise_data["content_id"])
        ):
            franchise = Franchise(content_id=franchise_data["content_id"])

        updated = utils.from_timestamp(franchise_data["updated"])

        if updated == franchise.updated:
            continue

        franchise.scored_by = franchise_data["scored_by"]
        franchise.score = franchise_data["score"]

        anime_cache = await session.scalars(
            select(Anime).filter(
                Anime.content_id.in_(
                    [
                        entry["content_id"]
                        for entry in franchise_data["franchise_entries"]
                        if entry["content_type"] == constants.CONTENT_ANIME
                    ]
                )
            )
        )

        manga_cache = await session.scalars(
            select(Manga).filter(
                Manga.content_id.in_(
                    [
                        entry["content_id"]
                        for entry in franchise_data["franchise_entries"]
                        if entry["content_type"] == constants.CONTENT_MANGA
                    ]
                )
            )
        )

        novel_cache = await session.scalars(
            select(Novel).filter(
                Novel.content_id.in_(
                    [
                        entry["content_id"]
                        for entry in franchise_data["franchise_entries"]
                        if entry["content_type"] == constants.CONTENT_NOVEL
                    ]
                )
            )
        )

        update_content = []

        for anime in anime_cache:
            anime.franchise_relation = franchise
            update_content.append(anime)

        for manga in manga_cache:
            manga.franchise_relation = franchise
            update_content.append(manga)

        for novel in novel_cache:
            novel.franchise_relation = franchise
            update_content.append(novel)

        franchise.relations = build_relations(franchise_data.get("entries", []))
        franchise.updated = updated

        session.add(franchise)
        session.add_all(update_content)
        await session.commit()

        # print(f"Processed franchise {franchise.content_id}")
