from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional


class AuthLoginSchema(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=100)


class TokenSchema(BaseModel):
    token: str = Field(min_length=1, max_length=500)


class UserLoginSchema(BaseModel):
    username: Optional[str] = None


class TokenResultSchema(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class JwtIdentitySchema(BaseModel):
    identity: Optional[str] = None


class JwtTokenSchema(BaseModel):
    token: Optional[str] = None


class ValidateTokenSchema(BaseModel):
    is_valid: Optional[bool] = None
    identity: Optional[str] = None
