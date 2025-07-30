from typing import Generic
from fastapi.params import Depends
from fastauth.models import UM
from fastauth.types import ID
from fastauth.exceptions import FastAuthException, status
from fastauth.schemas.auth import TokenType, TokenData, TokenResponse
from fastauth.settings import FastAuthSettings
from fastauth.types import DependencyCallable
from fastauth.services.auth import BaseAuthService
from fastauth.transport.base import BaseTransport


class FastAuth(Generic[UM, ID]):
    def __init__(
        self,
        settings: FastAuthSettings,
        service_dep: DependencyCallable[BaseAuthService[UM, ID]],
        transport: BaseTransport,
    ):
        self.settings = settings
        self.service_dep = service_dep
        self.transport = transport

    def get_access_token(self):
        return self.__get_token(TokenType.ACCESS)

    def get_refresh_token(self):
        return self.__get_token(TokenType.REFRESH)

    def get_current_user(self):
        async def _get_current_user(
            token_payload: TokenData = Depends(self.get_access_token()),
            service: BaseAuthService = Depends(self.service_dep),
        ):
            return await service.authenticate(token_payload)

        return _get_current_user

    def require_permission(self, permission: str):
        async def _require_permission(
            token_payload: TokenData = Depends(self.get_access_token()),
            service: BaseAuthService = Depends(self.service_dep),
        ):
            if not service.has_permission(token_payload.permissions, permission):
                raise FastAuthException(
                    status.HTTP_403_FORBIDDEN,
                    "Access denied",
                    f"Insufficient permission. Required: {permission}",
                )
            return await service.authenticate(token_payload)

        return _require_permission

    def require_role(self, role: str):
        async def _require_permission(
            token_payload: TokenData = Depends(self.get_access_token()),
            service: BaseAuthService = Depends(self.service_dep),
        ):
            if not service.has_role(token_payload.roles, role):
                raise FastAuthException(
                    status.HTTP_403_FORBIDDEN,
                    "Access denied",
                    f"Insufficient role. Required: {role}",
                )
            return await service.authenticate(token_payload)

        return _require_permission

    def require_any_permission(self, permissions: list[str]):
        async def _require_permission(
            token_payload: TokenData = Depends(self.get_access_token()),
            service: BaseAuthService = Depends(self.service_dep),
        ):
            if not any(
                service.has_permission(token_payload.permissions, perm)
                for perm in permissions
            ):
                raise FastAuthException(
                    status.HTTP_403_FORBIDDEN,
                    "Access denied",
                    f"Insufficient permissions. Required: {','.join(permissions)}",
                )
            return await service.authenticate(token_payload)

        return _require_permission

    def require_all_permissions(self, permissions: list[str]):
        async def _require_all_permission(
            token_payload: TokenData = Depends(self.get_access_token()),
            service: BaseAuthService = Depends(self.service_dep),
        ):
            if not all(
                service.has_permission(token_payload.permissions, perm)
                for perm in permissions
            ):
                raise FastAuthException(
                    status.HTTP_403_FORBIDDEN,
                    "Access denied",
                    f"Insufficient permissions. Required: {','.join(permissions)}",
                )
            return await service.authenticate(token_payload)

        return _require_all_permission

    def __get_token(self, token_type: TokenType):
        async def _check_token_internal(
            token: str = Depends(self.transport.get_schema()),
            service: BaseAuthService = Depends(self.service_dep),
        ):
            return await service.verify_token(token, token_type)

        return _check_token_internal

    def get_login_response(self, tokens: TokenResponse):
        return self.transport.login_response(tokens)

    def get_logout_response(self):
        return self.transport.logout_response()
