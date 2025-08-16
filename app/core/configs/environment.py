"""
Module to load all Environment variables
"""

from pydantic_settings import BaseSettings


class Environment(BaseSettings):
    """
    Environment, add the variable and its type here matching the .env file
    """

    # APPLICATION
    APPLICATION_NAME: str = "Barriil Club API"
    APPLICATION_HOST: str = "localhost"
    APPLICATION_PORT: int = 8000
    ENVIRONMENT: str = "local"
    RELEASE: str = "0.0.1"

    # DATABASE
    DATABASE_HOST: str = "localhost"

    # AUTH0
    AUTH0_DOMAIN: str | None = None
    AUTH0_API_AUDIENCE: str | None = None
    AUTH0_ISSUER: str | None = None
    AUTH0_ALGORITHMS: str | None = None
    AUTH0_CLIENT_ID: str | None = None
    AUTH0_CLIENT_SECRET: str | None = None
    APP_SECRET_KEY: str | None = None
    AUTH0_MANAGEMENT_API_CLIENT_ID: str | None = None
    AUTH0_MANAGEMENT_API_CLIENT_SECRET: str | None = None
    AUTH0_MANAGEMENT_API_AUDIENCE: str | None = None

    # SENTRY
    SENTRY_DSN: str | None = None


    class Config:
        """Load config file"""

        env_file = ".env"
        extra='ignore'
