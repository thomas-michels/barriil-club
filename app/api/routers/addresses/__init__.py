from fastapi import APIRouter
from .command_routers import router as command_router
from .query_routers import router as query_router


address_router = APIRouter()
address_router.include_router(command_router)
address_router.include_router(query_router)
