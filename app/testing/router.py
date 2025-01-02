from .schemas import DocumentArgs
from fastapi import APIRouter


router = APIRouter()


@router.post("/testing")
async def testing(args: DocumentArgs):
    return args
