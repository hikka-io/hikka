from fastapi import APIRouter, Depends
from app.database import get_session


router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("")
async def search_companies(
    # session: AsyncSession = Depends(get_session),
    # search: AnimeSearchArgs = Depends(validate_search_anime),
):
    return {}
