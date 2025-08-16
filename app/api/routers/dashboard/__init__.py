from fastapi import APIRouter
from .query_routers import router as query_router


dashboard_router = APIRouter()
dashboard_router.include_router(query_router)
