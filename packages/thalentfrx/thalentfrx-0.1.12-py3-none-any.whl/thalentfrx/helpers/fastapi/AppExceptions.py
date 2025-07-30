import shortuuid
from typing import Any, Dict
from fastapi import HTTPException, WebSocketException, status


# credentials_http_exception = HTTPException(
#     status_code=status.HTTP_401_UNAUTHORIZED,
#     detail="Could not validate credentials",
#     headers={"WWW-Authenticate": "Bearer"},
# )


class AppException(Exception):

    def __init__(
            self,
            status_code: int,
            detail: str,
    ):
        # Call the base class constructor with the parameters it needs
        log_id = shortuuid.uuid()
        detail = f'{detail} (id: {log_id})'
        super().__init__(detail)
        self.log_id = log_id
        self.status_code = status_code
        self.detail = detail

    def __str__(self):
        return self.detail


class WebSocketAppException(WebSocketException):
    def __init__(
            self,
            status_code: int,
            detail: str,
    ):
        # Call the base class constructor with the parameters it needs
        log_id = shortuuid.uuid()
        detail = f'{detail} (id: {log_id})'
        super().__init__(code=status_code, reason=detail)
        self.log_id = log_id
        self.status_code = status_code
        self.detail = detail

    def __str__(self):
        return self.detail


class InvalidTokenException(AppException):
    pass


class InvalidTokenWebSocketException(WebSocketAppException):
    pass


class CredentialException(AppException):
    pass

class UnexpectedException(AppException):
    pass

class IntegrationException(AppException):
    pass



def app_http_exception(
        app_exception: AppException,
        headers: Dict[str, str] = None,
) -> HTTPException:
    return HTTPException(
        status_code=app_exception.status_code,
        detail=app_exception.detail,
        headers=headers,
    )


def http_exception(
        status_code: int,
        detail: Any,
        headers: Dict[str, str] = None,
) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers=headers,
    )


def credential_exception() -> CredentialException:
    detail = "Invalid username or password."
    return CredentialException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
    )


def token_exception() -> InvalidTokenException:
    detail = "Invalid token."
    return InvalidTokenException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
    )


def token_web_socket_exception() -> InvalidTokenWebSocketException:
    detail = "Invalid token."
    return InvalidTokenWebSocketException(
        status_code=status.WS_1008_POLICY_VIOLATION,
        detail=detail,
    )


def not_found_exception(object_name: str) -> AppException:
    return AppException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{object_name} not found.",
    )


def integration_exception(detail: str) -> AppException:
    return IntegrationException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
    )


def general_exception(status_code: status, detail: str) -> AppException:
    return AppException(
        status_code=status_code,
        detail=detail,
    )
