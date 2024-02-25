from fastapi import APIRouter

from .amm2 import router as auth_router
from .amm2 import auth_user_router


router = APIRouter()


router.include_router(router=auth_router, prefix="/auth")
router.include_router(router=auth_user_router)
