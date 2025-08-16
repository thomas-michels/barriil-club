import jwt
from threading import Lock
from _thread import LockType
from cachetools import TTLCache
from fastapi.security import SecurityScopes
from jwt import PyJWKClient, decode
from jwt.exceptions import PyJWKClientError, DecodeError
from app.api.exceptions.authentication_exceptions import UnauthorizedException
from app.core.configs import get_environment

_env = get_environment()


class ValidateToken:

    def __init__(
        self,
        jwks_cache: TTLCache | None = None,
        jwks_lock: LockType | None = None,
    ) -> None:
        jwks_url = f'{_env.AUTH0_DOMAIN}/.well-known/jwks.json'
        self.jwks_client = PyJWKClient(jwks_url)

        self.algorithms = _env.AUTH0_ALGORITHMS
        self.audience = _env.AUTH0_API_AUDIENCE
        self.issuer = f"{_env.AUTH0_DOMAIN}/"

        self._cache = jwks_cache or TTLCache(
            maxsize=5,
            ttl=3600,
        )
        self._lock = jwks_lock or Lock()

    async def verify(self, scopes: SecurityScopes, token: str) -> dict:
        if not token:
            raise UnauthorizedException("Token not provided")

        kid = self._extract_kid(token=token)
        key = self._get_signing_key(kid=kid, token=token)

        return self._decode_token(token=token, key=key)

    def _extract_kid(self, token: str) -> str:
        try:
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")

            if not kid:
                raise UnauthorizedException("Token missing 'kid' in header")

            return kid

        except Exception as err:
            raise UnauthorizedException(f"Invalid header: {err}")

    def _get_signing_key(self, kid: str, token: str):
        with self._lock:
            key = self._cache.get(kid)

        if key:
            return key

        try:
            jwk = self.jwks_client.get_signing_key_from_jwt(token)
            key = jwk.key

            with self._lock:
                self._cache[kid] = key

            return key

        except (PyJWKClientError, DecodeError) as err:
            raise UnauthorizedException(f"Failed to retrieve JWKS signing key: {err}")

    def _decode_token(self, token: str, key) -> dict:
        try:
            return decode(
                token,
                key,
                algorithms=self.algorithms,
                audience=self.audience,
                issuer=self.issuer,
            )

        except Exception as err:
            raise UnauthorizedException(f"Failed to decode token: {err}")
