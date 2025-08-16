from datetime import timedelta

from fastapi import Request

from app.core.configs import get_environment, get_logger
from app.core.exceptions.internal import InternalErrorException
from app.core.utils.http_client import HTTPClient
from app.core.utils.utc_datetime import UTCDateTime

_env = get_environment()
logger = get_logger(__name__)


async def get_access_token(request: Request) -> str:
    logger.info("Getting access token")

    stored_access_token = request.app.state.access_token

    if stored_access_token and UTCDateTime.now() < stored_access_token["expires_at"]:
        logger.info("Using cached access token")
        return f"Bearer {stored_access_token['access_token']}"

    logger.info("Validating new access token from request headers")
    access_token = generate_new_access_token()

    expires_at = UTCDateTime.now() + timedelta(
        seconds=access_token.get("expires_in", 3600)
    )
    access_token["expires_at"] = expires_at

    request.app.state.access_token = access_token

    return f"Bearer {access_token['access_token']}"


def generate_new_access_token() -> dict:
    headers = {"content-type": "application/x-www-form-urlencoded"}

    payload = {
        "grant_type": "client_credentials",
        "client_id": _env.AUTH0_MANAGEMENT_API_CLIENT_ID,
        "client_secret": _env.AUTH0_MANAGEMENT_API_CLIENT_SECRET,
        "audience": f"https://{_env.AUTH0_MANAGEMENT_API_AUDIENCE}/api/v2/",
    }

    http_client = HTTPClient(headers=headers)

    status_code, response = http_client.post(
        url=f"{_env.AUTH0_DOMAIN}/oauth/token", data=payload
    )

    match status_code:
        case 200:
            return response

        case _:
            logger.error("Failed to generate an access token in Auth0")
            logger.error(f"payload: {payload}")
            logger.error(f"url: {_env.AUTH0_DOMAIN}/oauth/token")
            logger.error(f"status_code: {status_code} - response: {response}")
            raise InternalErrorException(message="Internal authentication error!")
