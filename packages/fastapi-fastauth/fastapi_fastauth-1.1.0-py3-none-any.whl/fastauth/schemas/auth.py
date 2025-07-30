from pydantic import BaseModel
from enum import StrEnum


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenData(BaseModel):
    user_id: str
    email: str
    roles: list[str] = []
    permissions: list[str] = []
    token_type: TokenType
    expires_in: int | None = None
    jti: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    username: str
    password: str


class ResetPasswordRequest(BaseModel):
    new_password: str
    token: str
