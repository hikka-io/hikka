from .responses import FavouriteResponse, DeleteResponse
from ..models import User, Anime, AnimeFavourite
from fastapi import APIRouter, Depends
from ..decorators import auth_required
from datetime import datetime
from ..errors import Abort

router = APIRouter(prefix="/favourite")

@router.get("/{slug}", response_model=FavouriteResponse)
async def get_favourite(
    slug: str, user: User = Depends(auth_required())
):
    # Find anime by slug
    if not (anime := await Anime.filter(slug=slug).first()):
        raise Abort("anime", "not-found")

    # Find user favourite anime record 
    if not (favourite := await AnimeFavourite.filter(**{
        "anime": anime, "user": user
    }).first()):
        raise Abort("favourite", "not-found")

    # Return record
    return {
        "created": favourite.created,
    }

@router.put("/{slug}", response_model=FavouriteResponse)
async def add_favourite(
    slug: str, user: User = Depends(auth_required())
):
    # Find anime by slug
    if not (anime := await Anime.filter(slug=slug).first()):
        raise Abort("anime", "not-found")

    # Make sure there is no favourite record for given anime
    if (favourite := await AnimeFavourite.filter(**{
        "anime": anime, "user": user
    }).first()):
        raise Abort("favourite", "exists")

    # Create record
    favourite = await AnimeFavourite.create(**{
        "created": datetime.utcnow(),
        "anime": anime,
        "user": user
    })

    # Return record
    return {
        "created": favourite.created,
    }

@router.delete("/{slug}", response_model=DeleteResponse)
async def delete_favourite(
    slug: str, user: User = Depends(auth_required())
):
    # Find anime by slug
    if not (anime := await Anime.filter(slug=slug).first()):
        raise Abort("anime", "not-found")

    # Make sure favourite record exists
    if not (favourite := await AnimeFavourite.filter(**{
        "anime": anime, "user": user
    }).first()):
        raise Abort("favourite", "not-found")

    # Delete record
    await favourite.delete()

    # Status response
    return {"success": True}
