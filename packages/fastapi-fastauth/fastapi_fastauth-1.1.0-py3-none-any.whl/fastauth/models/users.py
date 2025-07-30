from typing import Protocol, TypeVar
from fastauth.types import ID
from .rbac import IRole
from .oauth import IOAuth


class IUser(Protocol[ID]):
    id: ID
    email: str
    is_active: bool
    is_verified: bool
    hashed_password: str


UM = TypeVar("UM", bound=IUser)


class IRPUser(IUser[ID], Protocol[ID]):
    roles: list[IRole]


URPM = TypeVar("URPM", bound=IRPUser)


class IOAuthUser(IUser[ID], Protocol[ID]):
    oauth_accounts: list[IOAuth]


UOAM = TypeVar("UOAM", bound=IOAuthUser)


class IFullUser(IRPUser[ID], IOAuthUser[ID], Protocol[ID]):
    pass


UFM = TypeVar("UFM", bound=IFullUser)
