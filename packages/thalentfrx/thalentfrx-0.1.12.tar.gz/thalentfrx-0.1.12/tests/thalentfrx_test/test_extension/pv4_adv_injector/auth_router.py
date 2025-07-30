from typing import Any, Type

from fastapi import (
    APIRouter,
    status
)
from injector import Injector

from thalentfrx.core.services.AuthBaseService import AuthBaseService
from .auth_service import auth_service
from thalentfrx.core.injector.InjectorModule import InjectorModule

auth_router = APIRouter(prefix="/v1/authtestadvinjector2", tags=["Auth"])

inj_mod = InjectorModule()

auth_service = auth_service()
binder_map = {AuthBaseService: auth_service}
inj_mod.set_mapping(binder_map=binder_map)

inj = Injector([inj_mod])

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