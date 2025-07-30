import logging
import traceback
from html import escape
from functools import wraps
from logging import Logger
from typing import Dict, Optional, Mapping

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

from thalentfrx.helpers.fastapi.AppExceptions import (
    AppException,
    CredentialException,
    InvalidTokenException,
    app_http_exception,
    http_exception, UnexpectedException,
)


def __message_response(status_code: int, detail: str, headers: Optional[Mapping[str, str]] = None) -> (JSONResponse,
                                                                                                       str):
    response_json = JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({"detail": detail}),
        headers=headers,
    )
    # response_txt = PlainTextResponse(status_code=status_code, content=detail, headers=headers)
    response_txt = f'{detail}'
    return response_json, response_txt


def http_exception_handler(app):  # all, only_admin
    """Http exception handler decorator as alternative exception handler for fastapi built-in exception handler mechanism.

    Example:

    @UserRouterExt.post("/token/refresh", status_code=status.HTTP_200_OK, response_model=TokenResultSchema)
    @http_exception_handler()
    def token_refresh(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Session = Depends(get_db_session),
    ) -> Any:

        ...

    Args:
        app:
    """
    logger = app.logger

    def wrapper(fn):
        def log_exception(ex, level=logging.ERROR):
            logger.log(level, msg=ex.__str__(), exc_info=True)

        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except InvalidTokenException as ex:
                log_exception(ex, logging.WARNING)

                raise app_http_exception(
                    ex,
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except CredentialException as ex:
                log_exception(ex, logging.WARNING)
                raise app_http_exception(
                    ex,
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except AppException as ex:
                log_exception(ex, logging.WARNING)
                raise app_http_exception(ex)

            except RequestValidationError as ex:
                ex = UnexpectedException(status_code=400, detail=ex.__str__())
                log_exception(ex, logging.WARNING)
                raise http_exception(
                    status_code=400, detail=ex.__str__()
                )
            except StarletteHTTPException as ex:
                ex = UnexpectedException(status_code=ex.status_code, detail=ex.__str__())
                log_exception(ex, logging.WARNING)
                raise http_exception(
                    status_code=ex.status_code, detail=ex.__str__()
                )
            except ValueError as ex:
                ex = UnexpectedException(status_code=400, detail=ex.__str__())
                log_exception(ex, logging.WARNING)
                raise http_exception(
                    status_code=400, detail=ex.__str__()
                )
            except Exception as ex:
                ex = UnexpectedException(status_code=500, detail=ex.__str__())
                log_exception(ex, logging.WARNING)
                raise http_exception(
                    status_code=500, detail=ex.__str__()
                )

        return decorator

    return wrapper


def set_custom_exception_handler(app) -> None:
    logger: Logger | None = app.logger

    headers: Dict[str, str] = {
        "WWW-Authenticate": "Bearer"
    }

    @app.exception_handler(AppException)
    async def app_exception_handler(
            request: Request,
            exc: AppException
    ):
        response_json, response_txt = __message_response(status_code=exc.status_code, detail=exc.__str__())
        sanitized_response = escape(response_txt)
        logger.warning(msg=sanitized_response, exc_info=True)
        return response_json

    @app.exception_handler(InvalidTokenException)
    async def invalid_token_exception_handler(
            request: Request,
            exc: InvalidTokenException
    ):
        response_json, response_txt = __message_response(status_code=exc.status_code, detail=exc.__str__(),
                                                         headers=headers)
        sanitized_response = escape(response_txt)
        logger.warning(msg=sanitized_response, exc_info=True)
        return response_json

    @app.exception_handler(CredentialException)
    async def credential_exception_handler(
            request: Request,
            exc: CredentialException
    ):
        response_json, response_txt = __message_response(status_code=exc.status_code, detail=exc.__str__(),
                                                         headers=headers)
        sanitized_response = escape(response_txt)
        logger.warning(msg=sanitized_response, exc_info=True)
        return response_json

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        ex = UnexpectedException(exc.status_code, exc.detail)
        response_json, response_txt = __message_response(status_code=ex.status_code, detail=ex.__str__())
        sanitized_response = escape(response_txt)
        logger.warning(msg=sanitized_response, exc_info=True)
        return response_json

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        ex = UnexpectedException(422, detail=exc.__str__())
        response_json, response_txt = __message_response(status_code=ex.status_code, detail=ex.__str__())
        sanitized_response = escape(response_txt)
        logger.warning(msg=sanitized_response, exc_info=True)
        return response_json

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        if (
                request.url.path == "/v1/users/login"
                or request.url.path == "/v1/users/token/refresh"
        ):
            current_headers = {}
        else:
            current_headers = headers

        status_code = 500
        if isinstance(exc, HTTPException):
            status_code = exc.status_code
        ex = UnexpectedException(status_code, detail="An unexpected error occurred")

        response_json, response_txt = __message_response(status_code=ex.status_code, detail=ex.__str__(),
                                                         headers=current_headers)
        sanitized_response = escape(f"Unexpected error: {exc.__str__()}")
        logger.error(msg=sanitized_response, exc_info=True)
        logger.error(f"Traceback: {traceback.format_exc()}")
        return response_json
