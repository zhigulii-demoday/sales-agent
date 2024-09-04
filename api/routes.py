from fastapi import APIRouter
from . import  platforms, messages



router = APIRouter()
router.include_router(platforms.router, prefix="/platforms")
router.include_router(messages.messages_router, prefix="/messages")
