import logging
from logging import Logger
from typing import TypeVar, Generic, List

from fastapi import FastAPI, APIRouter
from pydantic_settings import BaseSettings

from thalentfrx.helpers.fastapi.ExceptionHandlers import set_custom_exception_handler
from thalentfrx.configs.Logger import get_logger
from thalentfrx.helpers.StartUpInfo import show_startup_info
import thalentfrx

T = TypeVar('T', bound=BaseSettings)


class ThalentFrx(FastAPI, Generic[T]):
    default_logger: Logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        # Instantiate FastAPI
        super().__init__(*args, **kwargs)
        self.uvicorn_logger: Logger | None = None
        self.logger: Logger | None = None
        self.env: T | None = None

    def environment_init(self, env: T = None):
        try:
            if env is None:
                raise ValueError("Environment configuration is required")
            self.env = env
            self.version = thalentfrx.__version__
            self.title = env.APP_NAME
        except Exception as e:
            self.default_logger.error(f"Error initializing environment: {e}")
            raise e

    def logger_init(self, env: T = None):
        try:
            if env is None:
                raise ValueError("Environment configuration is required for logger initialization")
            self.logger = get_logger(name=__name__)
            self.uvicorn_logger = logging.getLogger("uvicorn.error")
            set_custom_exception_handler(app=self)
            show_startup_info(app=self, env=env)
        except Exception as e:
            self.default_logger.error(f"Error initializing logger: {e}")
            raise e

    def router_init(self, routers: List[APIRouter]) -> None:
        for router in routers:
            self.include_router(router)
