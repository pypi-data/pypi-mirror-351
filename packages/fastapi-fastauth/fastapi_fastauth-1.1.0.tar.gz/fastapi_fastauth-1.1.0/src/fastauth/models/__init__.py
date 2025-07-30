from .users import IUser, IRPUser, IOAuthUser, IFullUser, UM, UFM, UOAM, URPM
from .rbac import IRole, IPermission, RM, PM
from .oauth import IOAuth, OAM
from typing import TypeVar

M = TypeVar(
    "M", bound=IUser | IRPUser | IOAuthUser | IFullUser | IRole | IPermission | IOAuth
)

__all__ = [
    "IUser",
    "IRPUser",
    "IOAuthUser",
    "IFullUser",
    "IRole",
    "IPermission",
    "IOAuth",
    "UM",
    "UFM",
    "UOAM",
    "URPM",
    "RM",
    "PM",
    "OAM",
    "M",
]
