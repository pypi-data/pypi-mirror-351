from pydantic_settings import BaseSettings
from pydantic import Field


class FastAuthSettings(BaseSettings):
    DEBUG: bool = True

    ALLOW_INACTIVE_USERS: bool = Field(default_factory=lambda e: e.get("DEBUG"))
    ALLOW_UNVERIFIED_USERS: bool = Field(default_factory=lambda e: e.get("DEBUG"))
    DEFAULT_USER_IS_ACTIVE: bool = True
    DEFAULT_USER_IS_VERIFIED: bool = False
    OAUTH_ASSOCIATE_BY_EMAIL: bool = False
    DEFAULT_USER_ROLES: list[str] = ["USER"]
    USER_LOGIN_FIELDS: list[str] = ["email"]
    USE_REFRESH_TOKEN: bool = True

    # ROUTER
    LOGIN_URL: str = "/api/auth/login"
    ROUTER_AUTH_PREFIX: str = "/auth"
    ROUTER_USERS_PREFIX: str = "/users"

    # JWT
    SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24
    ACCESS_TOKEN_AUDIENCE: list[str] = ["fastauth:auth"]
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 30
    STATE_TOKEN_AUDIENCE: list[str] = ["fastauth:state"]
    STATE_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 10
    VERIFICATION_TOKEN_AUDIENCE: list[str] = ["fastauth:verification"]
    VERIFICATION_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 10
    RESET_TOKEN_AUDIENCE: list[str] = ["fastauth:reset"]
    RESET_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 10

    # COOKIES
    COOKIE_ACCESS_TOKEN_NAME: str = "access_token"
    COOKIE_REFRESH_TOKEN_NAME: str = "refresh_token"
    COOKIE_ACCESS_TOKEN_MAX_AGE: int = Field(
        default_factory=lambda e: e.get("ACCESS_TOKEN_EXPIRE_SECONDS")
    )
    COOKIE_REFRESH_TOKEN_MAX_AGE: int = Field(
        default_factory=lambda e: e.get("REFRESH_TOKEN_EXPIRE_SECONDS")
    )
