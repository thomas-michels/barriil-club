from fastapi import APIRouter
from .command_routers import router as command_router
from .query_routers import router as query_router


company_router = APIRouter()
company_router.include_router(command_router)
company_router.include_router(query_router)
