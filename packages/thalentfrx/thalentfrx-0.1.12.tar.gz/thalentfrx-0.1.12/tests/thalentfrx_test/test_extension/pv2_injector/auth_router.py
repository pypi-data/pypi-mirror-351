from typing import Any

from fastapi import (
    APIRouter,
    status
)
from injector import Injector

from thalentfrx.core.services.AuthBaseService import AuthBaseService
from .auth_service_module import auth_service_module

auth_router = APIRouter(prefix="/v1/authtestinjector", tags=["Auth"])

inj = Injector([auth_service_module()])
service = inj.get(AuthBaseService)

@auth_router.get(
    "/hello",
    status_code=status.HTTP_200_OK,
    response_model=str,
)
def hello_world() -> Any:
    return "Hello World! from auth_router"


@auth_router.get(
    "/hellochild",
    status_code=status.HTTP_200_OK,
    response_model=None,
)
def hello_world_child() -> Any:
    return service.hello_world()