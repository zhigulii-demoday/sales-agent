from fastapi import APIRouter
from . import platforms, logs, companies
from . import messages



router = APIRouter()
router.include_router(platforms.router, prefix="/platforms")
router.include_router(logs.router, prefix="/logs")
router.include_router(companies.router, prefix="/companies")
#router.include_router(platforms.router, prefix="/platforms")
router.include_router(messages.messages_router, prefix="/messages")
