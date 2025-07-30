import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, List, Annotated, Union

import jwt
from fastapi import Depends, Query, Cookie
from fastapi.security import OAuth2PasswordBearer

from thalentfrx.configs.Environment import (
    get_environment_variables,
)
from thalentfrx.helpers.fastapi import AppExceptions


class AuthHelper:

    def __init__(self) -> None:
        pass

    @staticmethod
    def encode_token(
            token_type: str,
            identity: str,
            key: str,
            duration: int,
            scope: List[str] = None,
    ) -> str:
        # type = "access" or "refresh"
        now = datetime.now(timezone.utc)

        exp_date: datetime = now + timedelta(
            seconds=float(duration)
        )

        print(f'EXP DATE: {exp_date}')

        exp_date_unix: float = exp_date.timestamp()

        print(f'EXP DATE UNIX: {exp_date_unix}')

        token_data = {
            "iat": now,
            "jti": str(uuid.uuid4()),
            "type": token_type,
            "sub": identity,
            "exp": exp_date_unix,
            "iss": "urn:dnb",
            "aud": ["urn:dnb"],
            "scope": scope,
        }

        encoded: str = jwt.encode(
            token_data,
            key,
            algorithm="HS256",
            headers={"identity": identity},
        )
        return encoded

    @staticmethod
    def decode_token(token: str, key: str) -> Any:

        return jwt.decode(
            token,
            key,
            algorithms="HS256",
            verify=True,
            audience=["urn:dnb"],
            issuer="urn:dnb",
            leeway=0,
            options={
                "verify_signature": True,
                "require": [
                    "exp",
                    "iat",
                    "iss",
                    "aud",
                    "sub",
                ],
                "verify_exp": True,
                "verify_iat": True,
                "verify_iss": True,
                "verify_aud": True,
            },
        )

    @staticmethod
    def token_validate(token: str, allowed_scope: List[str] = None) -> tuple[str, list[str]]:

        if allowed_scope is None:
            # ALL
            allowed_scope = ['*']

        env_ext = get_environment_variables()

        try:
            print(f'token: {token}')

            eval_token = token.replace('Bearer ', '').strip()
            print(f'eval_token: {eval_token}')

            key = env_ext.JWT_TOKEN_SECRET
            print(f'key: {key}')

            payload = AuthHelper.decode_token(
                token=eval_token, key=key
            )
            identity: str = payload["sub"]
            authorize_scope: List[str] = payload["scope"]

            print(f'sub: {identity}')
            print(f'scope: {authorize_scope}')

            # if one or more scope match then it is authorize to access the function.
            if '*' not in allowed_scope:
                print(f'allowed_scope: {allowed_scope}')
                authorize_count = 0
                for item in authorize_scope:
                    if item in allowed_scope:
                        authorize_count += 1

                if authorize_count == 0:
                    raise AppExceptions.token_exception()
            else:
                print(f'allowed_scope: * (all)')

            return identity, authorize_scope
        except Exception as ex:
            print(f'error: {ex}')
            raise AppExceptions.token_exception()


def jwt_required(
        is_optional: bool = False,
        is_refresh: bool = False,
        allowed_scope=None,
):
    """Helps to verify authorization token on request's header and add kwargs['identity'] which is register on token 'sub' payload,
    then add function argument 'identity' as string and defaul value is None.

    Example:

        @UserRouterExt.post("/token/test", status_code=status.HTTP_200_OK, response_model=None)
        @AuthHelper.jwt_required()
        def token_test(token: Annotated[str, Depends(oauth2_scheme)], identity: str = None) -> Any:
            return {"identity": identity}

    Args:
        is_optional (bool, optional): Set 'True' if token is optional. Defaults to False.
        is_refresh (bool, optional): Set 'True' if refresh token is the token should be passed. Defaults to False.
        scope (List[str], optional): Set to non-empty string array if need to limit the access authorization scope. Defaults to ['*'] which is allow all.
        :param is_refresh:
        :param is_optional:
        :param allowed_scope:
    """

    if allowed_scope is None:
        allowed_scope = ['*']

    def wrapper(fn):
        @wraps(fn)
        async def decorator(*args, **kwargs):
            env_ext = get_environment_variables()
            auth_helper = AuthHelper()

            token: str = kwargs["token"].strip()
            identity, authorize_scope = auth_helper.token_validate(token=token, allowed_scope=allowed_scope)

            kwargs["identity"] = identity
            kwargs["scope"] = authorize_scope

            return await fn(*args, **kwargs)

        return decorator

    return wrapper


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/v1/auth/login"
)


def auth_info(token: Annotated[str, Depends(oauth2_scheme)]) -> \
        tuple[str, list[str]]:
    identity, authorize_scope = AuthHelper.token_validate(token=token)
    return identity, authorize_scope


def auth_check(token: Annotated[str, Depends(oauth2_scheme)]) -> None:
    try:
        identity, authorize_scope = AuthHelper.token_validate(token=token)
    except Exception as ex:
        raise AppExceptions.token_exception()


def auth_web_socket_check(token: Annotated[Union[str, None], Query()] = None) -> None:
    try:
        identity, authorize_scope = AuthHelper.token_validate(token=f'Bearer {token}')
    except Exception as ex:
        raise AppExceptions.token_web_socket_exception()


def auth_web_socket_info(token: Annotated[Union[str, None], Query()] = None) -> \
        tuple[str, list[str]]:
    identity, authorize_scope = AuthHelper.token_validate(token=f'Bearer {token}')
    return identity, authorize_scope
