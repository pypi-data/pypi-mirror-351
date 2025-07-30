import uuid

from fastauth.models import IPermission, PM, RM, OAM
from fastauth.types import ID
from typing import Generic, TYPE_CHECKING, TypeVar
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from sqlalchemy import String, Boolean, UniqueConstraint, ForeignKey, Integer
from fastauth.contrib.sqlalchemy._generic import GUID

RID = TypeVar("RID")
PID = TypeVar("PID")


class BaseUserModel(Generic[ID]):
    __tablename__ = "users"
    __abstract__ = True

    if TYPE_CHECKING:
        id: ID
        email: str
        is_active: bool
        is_verified: bool
        hashed_password: str
    else:
        id: Mapped[ID] = mapped_column(primary_key=True)
        email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
        hashed_password: Mapped[str] = mapped_column(String(255))
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        is_verified: Mapped[bool] = mapped_column(Boolean, default=False)


class BaseUUIDUserModel(BaseUserModel[uuid.UUID]):
    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)


class BasePermissionModel(Generic[ID]):
    __tablename__ = "permissions"
    __abstract__ = True

    if TYPE_CHECKING:
        id: ID
        name: str | None
        description: str | None
        action: str
        resource: str
    else:
        id: Mapped[ID] = mapped_column(primary_key=True)
        name: Mapped[str | None]
        description: Mapped[str | None]
        action: Mapped[str] = mapped_column(String(255))
        resource: Mapped[str] = mapped_column(String(255))

    __table_args__ = (
        UniqueConstraint("resource", "action", name="uq_resource_action"),
    )


class BaseRoleModel(Generic[ID, PM]):
    __tablename__ = "roles"
    __abstract__ = True
    if TYPE_CHECKING:
        id: ID
        name: str
        permissions: list[IPermission]
    else:
        id: Mapped[ID] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(255), unique=True, index=True)

        @declared_attr
        def permissions(self) -> Mapped[list[PM]]:
            return relationship(secondary="role_permission_rel", lazy="selectin")


class BaseIntRoleModel(BaseRoleModel[int, PM]):
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)


class BaseIntPermissionModel(BasePermissionModel[int]):
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)


class BaseRolePermissionRel(Generic[RID, PID]):
    __tablename__ = "role_permission_rel"
    role_id: Mapped[RID] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[PID] = mapped_column(
        ForeignKey("permissions.id"), primary_key=True
    )


class BaseUserRoleRel(Generic[ID, RID]):
    __tablename__ = "user_role_rel"
    user_id: Mapped[ID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[RID] = mapped_column(ForeignKey("roles.id"), primary_key=True)


class BaseOAuthAccount(Generic[ID]):
    __tablename__ = "oauth_accounts"
    if TYPE_CHECKING:
        id: ID
        oauth_name: str
        access_token: str
        expires_at: int | None
        refresh_token: str | None
        account_id: str
        account_email: str
    else:
        id: Mapped[ID] = mapped_column(primary_key=True)
        oauth_name: Mapped[str] = mapped_column(String(255), index=True)
        account_id: Mapped[str] = mapped_column(String(255), index=True)
        account_email: Mapped[str] = mapped_column(String(255), index=True)
        access_token: Mapped[str]
        refresh_token: Mapped[str | None]
        expires_at: Mapped[int | None]

    @declared_attr
    def user_id(self) -> Mapped[ID]:
        return mapped_column(ForeignKey("users.id", ondelete="CASCADE"))


class BaseUUIDOAuthAccount(BaseOAuthAccount[uuid.UUID]):
    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("users.id", ondelete="CASCADE")
    )


class RBACMixin(Generic[RM]):
    __abstract__ = True

    @declared_attr
    def roles(self) -> Mapped[list[RM]]:
        return relationship(secondary="user_role_rel", lazy="selectin")


class OAuthMixin(Generic[OAM]):
    @declared_attr
    def oauth_accounts(self) -> Mapped[list[OAM]]:
        return relationship(lazy="selectin")
