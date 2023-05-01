from .responses import WatchResponse, WatchDeleteResponse
from ..models import User, Anime, AnimeWatch
from fastapi import APIRouter, Depends
from ..decorators import auth_required
from ..watch.args import WatchArgs
from datetime import datetime
from ..errors import Abort

router = APIRouter(prefix="/watch")

@router.get("/{slug}", response_model=WatchResponse)
async def get_watch(
    slug: str, user: User = Depends(auth_required())
):
    # Find anime by slug
    if not (anime := await Anime.filter(slug=slug).first()):
        raise Abort("anime", "not-found")

    # Find user watch record for anime 
    if not (watch := await AnimeWatch.filter(**{
        "anime": anime, "user": user
    }).first()):
        raise Abort("watch", "not-found")

    # Return watch record
    return {
        "reference": watch.reference,
        "note": watch.note,
        "user_score": watch.user_score,
        "created": watch.created,
        "updated": watch.updated,
        "episodes": watch.episodes,
        "status": watch.status,
    }

@router.put("/{slug}", response_model=WatchResponse)
async def add_watch(
    slug: str, args: WatchArgs, user: User = Depends(auth_required())
):
    # Find anime by slug
    if not (anime := await Anime.filter(slug=slug).first()):
        raise Abort("anime", "not-found")

    # User can't set more than 0 episodes if anime not yet aired
    if not anime.episodes and args.episodes > 0:
        raise Abort("watch", "bad-episodes")

    # Make sure user provided episodes within constraints
    if anime.episodes and args.episodes > anime.episodes:
        raise Abort("watch", "bad-episodes")

    # Create watch record if missing
    if not (watch := await AnimeWatch.filter(**{
        "anime": anime, "user": user
    }).first()):
        watch = AnimeWatch()
        watch.created = datetime.utcnow()
        watch.anime = anime
        watch.user = user

    # Set attributes from args to watch record
    for key, value in args.dict().items():
        setattr(watch, key, value)

    # Save watch record
    watch.updated = datetime.utcnow()
    await watch.save()

    # Return watch record
    return {
        "reference": watch.reference,
        "note": watch.note,
        "user_score": watch.user_score,
        "created": watch.created,
        "updated": watch.updated,
        "episodes": watch.episodes,
        "status": watch.status,
    }

@router.delete("/{slug}", response_model=WatchDeleteResponse)
async def delete_watch(
    slug: str, user: User = Depends(auth_required())
):
    # Find anime by slug
    if not (anime := await Anime.filter(slug=slug).first()):
        raise Abort("anime", "not-found")

    # Find anime watch record
    if not (watch := await AnimeWatch.filter(**{
        "anime": anime, "user": user
    }).first()):
        raise Abort("watch", "not-found")

    # And delete it
    await watch.delete()

    # Status response
    return {"success": True}
