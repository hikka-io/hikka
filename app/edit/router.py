from fastapi import APIRouter, Depends
from .dependencies import verify_test
from app.models import User

router = APIRouter(prefix="/edit", tags=["Edit"])


@router.get("/test")
async def test_role(
    user: User = Depends(verify_test),
):
    return user
