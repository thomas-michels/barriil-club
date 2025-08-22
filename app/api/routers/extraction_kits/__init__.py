from fastapi import APIRouter

from .command_routers import router as command_router
from .query_routers import router as query_router

extraction_kit_router = APIRouter()
extraction_kit_router.include_router(command_router)
extraction_kit_router.include_router(query_router)
