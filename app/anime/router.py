from .dependencies import get_anime_info
from fastapi import APIRouter, Depends
from app.models import Anime
from app import utils
from . import service


router = APIRouter(prefix="/anime")


@router.get("/{slug}")
async def anime_slug(anime: Anime = Depends(get_anime_info)):
    genres = [
        {"name_en": genre.name_en, "name_ua": genre.name_ua, "slug": genre.slug}
        for genre in anime.genres
    ]

    studios = [
        {"name": company.name, "slug": company.slug}
        for company in anime.studios
    ]

    producers = [
        {"name": company.name, "slug": company.slug}
        for company in anime.producers
    ]

    # Return full anime info
    return {
        "start_date": utils.to_timestamp(anime.start_date),
        "end_date": utils.to_timestamp(anime.end_date),
        "total_episodes": anime.total_episodes,
        "synopsis_en": anime.synopsis_en,
        "synopsis_ua": anime.synopsis_ua,
        "media_type": anime.media_type,
        "scored_by": anime.scored_by,
        "title_ja": anime.title_ja,
        "title_en": anime.title_en,
        "title_ua": anime.title_ua,
        "duration": anime.duration,
        "episodes": anime.episodes,
        "synonyms": anime.synonyms,
        "external": anime.external,
        "producers": producers,
        "rating": anime.rating,
        "source": anime.source,
        "status": anime.status,
        "videos": anime.videos,
        "score": anime.score,
        "stats": anime.stats,
        "studios": studios,
        "nsfw": anime.nsfw,
        "slug": anime.slug,
        "genres": genres,
        "ost": anime.ost,
    }
