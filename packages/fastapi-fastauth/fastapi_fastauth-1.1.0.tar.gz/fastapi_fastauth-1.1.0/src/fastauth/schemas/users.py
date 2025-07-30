from .base import ReadSchema, UpdateSchema, CreateSchema
from typing import Generic
from fastauth.types import ID
from pydantic import EmailStr


class BaseUserRead(ReadSchema, Generic[ID]):
    id: ID
    email: EmailStr
    is_active: bool
    is_verified: bool


class BaseUserCreate(CreateSchema):
    email: EmailStr
    password: str
    is_active: bool
    is_verified: bool
    roles: list[str] = []


class BaseUserUpdate(UpdateSchema):
    email: EmailStr | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
    roles: list[str] = []
