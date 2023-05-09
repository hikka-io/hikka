from .schemas import AnimeSearchArgs
from fastapi import APIRouter


router = APIRouter(prefix="/search")


@router.post("/anime")
async def search_anime(search: AnimeSearchArgs):
    return search
