from fastapi import APIRouter
from . import platforms, logs



router = APIRouter()
router.include_router(platforms.router, prefix="/platforms")
router.include_router(logs.router, prefix="/logs")
