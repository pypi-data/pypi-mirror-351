from typing import Any, Optional
from pydantic import BaseModel, Field

class LoginRequestDto(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=100)
    is_remember: bool = Field(default=False)


class TokenResponseDto(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class ValidateTokenResponseDto(BaseModel):
    status: Optional[bool] = None
    payload: Optional[Any] = None
