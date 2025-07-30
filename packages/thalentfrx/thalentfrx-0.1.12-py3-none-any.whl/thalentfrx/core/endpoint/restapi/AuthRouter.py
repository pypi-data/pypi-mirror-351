from typing import Any, Annotated, Optional, List

from fastapi import (
    APIRouter,
    status, Depends, Form, Request
)
from fastapi.security import OAuth2PasswordRequestForm

from thalentfrx.helpers.fastapi.AuthHelper import auth_info, auth_check, oauth2_scheme
from thalentfrx.core.endpoint.restapi.AuthSchema import TokenResultSchema, JwtTokenSchema, ValidateTokenSchema, \
    UserLoginSchema
from thalentfrx.core.services.AuthDto import TokenResponseDto, LoginRequestDto
from thalentfrx.core.services.AuthBaseService import AuthBaseService

AuthRouter = APIRouter(prefix="/v1/auth", tags=["Auth"])

service: AuthBaseService | None = None

@AuthRouter.get(
    "/hello",
    status_code=status.HTTP_200_OK,
    response_model=str,
)
def hello_world() -> Any:
    return "Hello World! from AuthRouter"


@AuthRouter.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=TokenResultSchema,
)
def login(
        form_data: Annotated[
            OAuth2PasswordRequestForm, Depends()
        ],
        is_remember: Annotated[Optional[bool], Form()] = False,
) -> Any:
    data: LoginRequestDto = LoginRequestDto(
        username=form_data.username,
        password=form_data.password,
        is_remember=is_remember
    )
    dto_response: TokenResponseDto = service.login(data)
    return dto_response


@AuthRouter.post(
    "/token/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenResultSchema,
    dependencies=[Depends(auth_check)],
)
def token_refresh(
        auth: Annotated[tuple[str, List[str]], Depends(auth_info)],
) -> Any:
    identity: str = auth[0]
    dto_response: TokenResponseDto = (
        service.refresh_token(identity=identity)
    )
    return dto_response


@AuthRouter.post(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserLoginSchema,
    dependencies=[Depends(auth_check)],
)
def get_current_active_user(
        auth: Annotated[tuple[str, List[str]], Depends(auth_info)],
) -> Any:
    identity: str = auth[0]
    return {"username": identity}


@AuthRouter.post(
    "/token",
    status_code=status.HTTP_200_OK,
    response_model=JwtTokenSchema,
    dependencies=[Depends(auth_check)],
)
def token(
        auth_token: Annotated[str, Depends(oauth2_scheme)]
) -> Any:
    return {"token": auth_token}


@AuthRouter.post(
    "/token/validate",
    status_code=status.HTTP_200_OK,
    response_model=ValidateTokenSchema,
    dependencies=[Depends(auth_check)]
)
def token_validate(
        auth: Annotated[tuple[str, List[str]], Depends(auth_info)],
) -> Any:
    identity: str = auth[0]
    authorize_scope: List[str] = auth[1]

    if identity:
        is_valid = True
    else:
        is_valid = False

    return {
        "is_valid": is_valid,
        "identity": identity,
        "authorize_scope": authorize_scope,
    }