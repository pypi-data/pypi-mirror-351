from .base import ReadSchema, CreateSchema
from typing import Generic
from fastauth.types import ID


class OAuthRead(ReadSchema, Generic[ID]):
    id: ID
    oauth_name: str
    access_token: str
    expires_at: int | None
    refresh_token: str | None
    account_id: str
    account_email: str


class OAuthCreate(CreateSchema):
    oauth_name: str
    access_token: str
    account_id: str
    account_email: str
    expires_at: int | None = None
    refresh_token: str | None = None


class OAuth2AuthorizeResponse(ReadSchema):
    authorization_url: str
