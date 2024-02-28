from fastapi import APIRouter

from .users import router as user_router
from .conversations import router as conversation_router
from .authorization import router as auth_router


router = APIRouter()

router.include_router(router=user_router, prefix="/users")
router.include_router(router=conversation_router, prefix="/conversations")
router.include_router(router=auth_router, prefix="/auth")

