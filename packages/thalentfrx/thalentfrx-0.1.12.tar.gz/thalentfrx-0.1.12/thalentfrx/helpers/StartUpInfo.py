from typing import TypeVar, Generic

from pydantic_settings import BaseSettings

from thalentfrx.configs.Logger import get_logger

T = TypeVar('T', bound=BaseSettings)

def show_startup_info(app, env: Generic[T]) -> None:
    logger = get_logger(name=__name__)

    logger.info("API is starting up.")
    logger.info(f"APP NAME: {env.APP_NAME}")
    logger.info(f"VERSION: {app.version}")

    logger.info(f"BASE_DIR: {env.BASE_DIR}")
    logger.info(f"ENV: {env.ENV}")

    logger.info(
        f"DATABASE_DIALECT: {env.DATABASE_DIALECT}"
    )
    logger.info(
        f"DATABASE_HOSTNAME: {env.DATABASE_HOSTNAME}"
    )
    logger.info(f"DATABASE_PORT: {env.DATABASE_PORT}")
    logger.info(f"DATABASE_SSL_MODE: {env.DATABASE_SSL_MODE}")
    logger.info(f"DATABASE_NAME: {env.DATABASE_NAME}")

    logger.debug(
        f"DATABASE_USERNAME: {env.DATABASE_USERNAME}"
    )
    logger.info(f"DEBUG_MODE: {env.DEBUG_MODE}")

    logger.info(f"LOG_CLI: {env.LOG_CLI}")
    logger.info(f"LOG_CLI_LEVEL: {env.LOG_CLI_LEVEL}")
    logger.info(f"LOG_FILE: {env.LOG_FILE}")
    logger.info(f"LOG_FILE_LEVEL: {env.LOG_FILE_LEVEL}")

    logger.info(
        f"JWT_ACCESS_TOKEN_DURATION_IN_SEC: {env.JWT_ACCESS_TOKEN_DURATION_IN_SEC}"
    )
    logger.info(
        f"JWT_ACCESS_TOKEN_REMEMBER_DURATION_IN_SEC: {env.JWT_ACCESS_TOKEN_REMEMBER_DURATION_IN_SEC}"
    )
    logger.info(
        f"JWT_REFRESH_TOKEN_DURATION_IN_SEC: {env.JWT_REFRESH_TOKEN_DURATION_IN_SEC}"
    )

    logger.info(f"LOG_FILE: {env.UVICORN_LOG_FILE_PATH}")
    logger.info(f"AUTH_SERVICE_MODULE_NAME: {env.AUTH_SERVICE_MODULE_NAME}")
    logger.info(f"AUTH_SERVICE_CLASS_NAME: {env.AUTH_SERVICE_CLASS_NAME}")

    if env.ENV != "prod":
        pass
        # logger.debug("TEST DEBUG")
        # logger.info("TEST INFO")
        # logger.warning("TEST WARNING")
        # logger.error("TEST ERROR")
        # logger.critical("TEST CRITICAL")
