from fastapi import APIRouter

from .users import router as user_router
from .conversations import router as conversation_router
from .authorization import router as auth_router
from .messages import router as message_router
from .chat import router as chat_router


router = APIRouter()

router.include_router(router=user_router, prefix="/users")
router.include_router(router=conversation_router, prefix="/conversations")
router.include_router(router=auth_router, prefix="/auth")
router.include_router(router=message_router, prefix="/messages")

router.include_router(router=chat_router, prefix="/chat")
