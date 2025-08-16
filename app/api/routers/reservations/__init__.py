from fastapi import APIRouter
from .command_routers import router as command_router
from .query_routers import router as query_router


reservation_router = APIRouter()
reservation_router.include_router(command_router)
reservation_router.include_router(query_router)
