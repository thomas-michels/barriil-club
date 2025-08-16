from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from cachetools import TTLCache
import threading

from app.api.dependencies.response import build_response

DEFAULT_LIMIT = 100  # máximo de requisições
DEFAULT_WINDOW = 60  # janela em segundos


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = DEFAULT_LIMIT, window: int = DEFAULT_WINDOW, maxsize: int = 100):
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.cache = TTLCache(maxsize=maxsize, ttl=window)
        self.lock = threading.Lock()

    async def dispatch(self, request: Request, call_next):
        client_ip = request.headers.get("fly-client-ip", request.client.host)

        with self.lock:
            count = self.cache.get(client_ip, 0) + 1
            self.cache[client_ip] = count

        if count > self.limit:
            return build_response(
                status_code=429,
                message="Too many requests"
            )

        response = await call_next(request)
        return response
