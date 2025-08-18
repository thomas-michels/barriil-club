from asgi_correlation_id import CorrelationIdMiddleware
import sentry_sdk
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.dependencies.response import build_response
from app.api.middleware.rate_limiting import RateLimitMiddleware
from app.api.routers import (
    user_router,
    extractor_router,
    company_router,
    address_router,
    customer_router,
    beer_type_router,
    keg_router,
    beer_dispenser_router,
    pressure_gauge_router,
    cylinder_router,
    reservation_router,
    dashboard_router,
)
from app.api.routers.exception_handlers import (
    unprocessable_entity_error_422,
    generic_error_500,
    not_found_error_404,
    generic_error_400,
)
from app.api.routers.exception_handlers.generic_errors import http_exception_handler
from app.core.db.connection import lifespan
from app.core.exceptions import UnprocessableEntity, NotFoundError, InvalidPassword
from app.core.configs import get_environment

_env = get_environment()


# sentry_sdk.init(
#     dsn=_env.SENTRY_DSN,
#     traces_sample_rate=1.0,
#     server_name=_env.APPLICATION_NAME,
#     release=_env.RELEASE,
#     environment=_env.ENVIRONMENT,
#     _experiments={
#         "continuous_profiling_auto_start": True,
#     },
# )


app = FastAPI(
    title=_env.APPLICATION_NAME,
    lifespan=lifespan,
    version=_env.RELEASE
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RateLimitMiddleware, limit=250, window=60)

app.include_router(user_router, prefix="/api")
app.include_router(extractor_router, prefix="/api")
app.include_router(company_router, prefix="/api")
app.include_router(address_router, prefix="/api")
app.include_router(customer_router, prefix="/api")
app.include_router(beer_type_router, prefix="/api")
app.include_router(keg_router, prefix="/api")
app.include_router(beer_dispenser_router, prefix="/api")
app.include_router(pressure_gauge_router, prefix="/api")
app.include_router(cylinder_router, prefix="/api")
app.include_router(reservation_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(UnprocessableEntity, unprocessable_entity_error_422)
app.add_exception_handler(NotFoundError, not_found_error_404)
app.add_exception_handler(InvalidPassword, generic_error_400)
app.add_exception_handler(Exception, generic_error_500)


@app.get("/")
async def root_path(request: Request):
    return build_response(status_code=200, message="I'm alive!", data=None)


@app.get("/health", tags=["Health Check"])
async def health_check():
    return build_response(status_code=200, message="I'm alive!", data=None)
