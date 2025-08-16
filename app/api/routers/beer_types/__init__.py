from fastapi import APIRouter
from .command_routers import router as command_router
from .query_routers import router as query_router


beer_type_router = APIRouter()
beer_type_router.include_router(command_router)
beer_type_router.include_router(query_router)
