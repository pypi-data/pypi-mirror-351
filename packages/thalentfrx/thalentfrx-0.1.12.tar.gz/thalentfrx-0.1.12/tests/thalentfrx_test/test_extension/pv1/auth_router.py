from typing import Any

from fastapi import (
    APIRouter,
    status
)

from .auth_service import auth_service

auth_router = APIRouter(prefix="/v1/authtest", tags=["Auth"])
service = auth_service()

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