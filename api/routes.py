from fastapi import APIRouter
from . import platforms



router = APIRouter()
router.include_router(platforms.router, prefix="/platforms")
