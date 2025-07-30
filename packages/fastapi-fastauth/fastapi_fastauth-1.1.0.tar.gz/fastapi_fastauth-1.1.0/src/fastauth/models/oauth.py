from typing import Protocol, TypeVar
from fastauth.types import ID


class IOAuth(Protocol[ID]):
    id: ID
    oauth_name: str
    access_token: str
    expires_at: int | None
    refresh_token: str | None
    account_id: str
    account_email: str


OAM = TypeVar("OAM", bound=IOAuth)
