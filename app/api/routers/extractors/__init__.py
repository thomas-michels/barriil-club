from fastapi import APIRouter
from .command_routers import router as command_router
from .query_routers import router as query_router


extractor_router = APIRouter()
extractor_router.include_router(command_router)
extractor_router.include_router(query_router)
