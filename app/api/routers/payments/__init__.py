from fastapi import APIRouter

from .query_routers import router as query_router

payment_router = APIRouter()
payment_router.include_router(query_router)
