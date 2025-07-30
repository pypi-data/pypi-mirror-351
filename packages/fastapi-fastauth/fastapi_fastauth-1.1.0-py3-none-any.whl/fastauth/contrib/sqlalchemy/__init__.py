try:
    import sqlalchemy  # noqa: F401
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "You need to install sqlalchemy, run `pip install fastapi-fastauth[sqlalchemy]`"
    )

from .models import (
    BaseUserModel,
    BaseRoleModel,
    BaseUUIDUserModel,
    BasePermissionModel,
    BaseIntRoleModel,
    BaseIntPermissionModel,
    BaseRolePermissionRel,
    BaseUserRoleRel,
    RBACMixin,
    BaseUUIDOAuthAccount,
    BaseOAuthAccount,
    OAuthMixin,
)
from .repositories import (
    SQLAlchemyBaseRepository,
    SQLAlchemyUserRepository,
    SQLAlchemyOAuthRepository,
)

__all__ = [
    "BaseUserModel",
    "BaseRoleModel",
    "BaseUUIDUserModel",
    "BasePermissionModel",
    "BaseIntRoleModel",
    "BaseIntPermissionModel",
    "BaseRolePermissionRel",
    "BaseUserRoleRel",
    "RBACMixin",
    "BaseUUIDOAuthAccount",
    "BaseOAuthAccount",
    "OAuthMixin",
    "SQLAlchemyBaseRepository",
    "SQLAlchemyUserRepository",
    "SQLAlchemyOAuthRepository",
]
