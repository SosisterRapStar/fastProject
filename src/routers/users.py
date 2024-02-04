from typing import List

from fastapi import APIRouter

from src.schemas.users import UserOut

router = APIRouter()
@router.get("/users/", tags=["users"], response_model=List[UserOut])
async def get_user():
