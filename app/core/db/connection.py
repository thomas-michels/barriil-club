from contextlib import asynccontextmanager
from threading import Lock

from cachetools import TTLCache
from fastapi import FastAPI
from mongoengine import connect

from app.api.dependencies.verify_token import ValidateToken
from app.core.configs import get_environment, get_logger

_env = get_environment()
_logger = get_logger(__name__)


def start_database():
    connetion = connect(
        host=_env.DATABASE_HOST
    )
    connetion.server_info()


@asynccontextmanager
async def lifespan(app: FastAPI) -> None: # type: ignore
    _logger.info("Connecting to MongoDB")

    app.state.jwks_key_cache = TTLCache(maxsize=5, ttl=3600)
    app.state.jwks_cache_lock = Lock()

    start_database()

    app.state.auth = ValidateToken(
        jwks_cache=app.state.jwks_key_cache,
        jwks_lock=app.state.jwks_cache_lock
    )
    app.state.access_token = None

    # Caches
    app.state.cached_users = {}

    _logger.info("Connection established")

    yield
