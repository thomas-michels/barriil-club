from fastapi import APIRouter
from .command_routers import router as command_router
from .query_routers import router as query_router


pressure_gauge_router = APIRouter()
pressure_gauge_router.include_router(command_router)
pressure_gauge_router.include_router(query_router)
