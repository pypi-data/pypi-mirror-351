import sys
from functools import lru_cache
import os

from pydantic_settings import SettingsConfigDict, BaseSettings


@lru_cache
def get_env_filename():
    # runtime_env = os.getenv("ENV")
    # return f".env.{runtime_env}" if runtime_env else ".env"
    return ".env"


def get_root_directory():
    """
    Retrieves the root directory of the application.

    It checks for the following cases:
    1. If the script is run directly, it returns the directory of the script.
    2. If the script is run as a module, it returns the package root directory.
    3. If running in a frozen environment (like PyInstaller), it returns the directory of the executable.
    """
    if getattr(sys, 'frozen', False):
        # Running in a frozen environment (e.g., PyInstaller)
        root_dir = os.path.dirname(sys.executable)
    elif __name__ == '__main__':
        # Running the script directly
        root_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        # Running as a module
        root_dir = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
    return root_dir


class EnvironmentSettings(BaseSettings):
    ENV: str = os.getenv("ENV")
    BASE_DIR: str = get_root_directory()
    APP_NAME: str = ''
    DATABASE_DIALECT: str = ''
    DATABASE_HOSTNAME: str = ''
    DATABASE_PORT: int = 0
    DATABASE_NAME: str = ''
    DATABASE_USERNAME: str = ''
    DATABASE_PASSWORD: str = ''
    DATABASE_SSL_MODE: bool = False
    DEBUG_MODE: bool = True

    LOG_CLI: bool = False
    LOG_CLI_LEVEL: str = ''
    LOG_CLI_FORMAT: str = ''
    LOG_CLI_DATE_FORMAT: str = ''

    LOG_FILE: str = ''
    LOG_FILE_MODE: str = ''
    LOG_FILE_LEVEL: str = ''
    LOG_FILE_FORMAT: str = ''
    LOG_FILE_DATE_FORMAT: str = ''
    LOG_FILE_MAX_BYTES: int = 0
    LOG_FILE_BACKUP_COUNT: int = 0

    LOG_FILE_DEBUG_PATH: str = ''
    LOG_FILE_WARNING_PATH: str = ''

    JWT_TOKEN_SECRET: str = ''
    JWT_ACCESS_TOKEN_DURATION_IN_SEC: int = 0
    JWT_ACCESS_TOKEN_REMEMBER_DURATION_IN_SEC: int = 0
    JWT_REFRESH_TOKEN_DURATION_IN_SEC: int = 0

    UVICORN_LOG_FILE_PATH: str = ''

    AUTH_SERVICE_MODULE_NAME: str = ''
    AUTH_SERVICE_CLASS_NAME: str = ''

    env_file: str = get_env_filename()
    model_config = SettingsConfigDict(env_file=env_file, env_file_encoding="utf-8")


@lru_cache
def get_environment_variables():
    return EnvironmentSettings()
