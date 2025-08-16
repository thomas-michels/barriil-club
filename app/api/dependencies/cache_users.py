from fastapi import Request
from app.core.configs import get_logger

logger = get_logger(__name__)


def get_cached_users(request: Request) -> dict:
    return request.app.state.cached_users
