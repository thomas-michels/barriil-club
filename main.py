import uvicorn

from app.core.configs import get_environment

_env = get_environment()


if __name__ == "__main__":
    uvicorn.run(
        "app.application:app",
        host=_env.APPLICATION_HOST,
        port=_env.APPLICATION_PORT,
        reload=True,
    )
