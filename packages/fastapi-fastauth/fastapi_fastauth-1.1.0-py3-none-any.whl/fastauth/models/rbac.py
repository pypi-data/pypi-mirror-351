from typing import Protocol, TypeVar
from fastauth.types import ID


class IPermission(Protocol[ID]):
    id: ID
    name: str | None
    description: str | None
    resource: str
    action: str


PM = TypeVar("PM", bound=IPermission)


class IRole(Protocol[ID]):
    id: ID
    name: str
    description: str | None
    permissions: list[IPermission]


RM = TypeVar("RM", bound=IRole)
