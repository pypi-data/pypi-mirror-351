from typing import Annotated

from fastauth.fastauth import FastAuth
from fastapi import Depends
from fastauth.schemas.auth import LoginRequest, TokenData
from fastauth.services import BaseAuthService
from fastauth.utils.router import default_router
from fastauth.transport.bearer import BearerTransport
from fastapi.security import OAuth2PasswordRequestForm


def create_auth_router(security: FastAuth, **kwargs):
    router = default_router(
        security.settings.ROUTER_AUTH_PREFIX, tags=["Auth"], **kwargs
    )

    if isinstance(security.transport, BearerTransport):
        credentials_type = Annotated[OAuth2PasswordRequestForm, Depends()]
    else:
        credentials_type = LoginRequest

    @router.post("/login")
    async def user_login(
        credentials: credentials_type,
        service: BaseAuthService = Depends(security.service_dep),
    ):
        tokens = await service.login(credentials.username, credentials.password)
        return security.get_login_response(tokens)

    @router.post("/logout", dependencies=[Depends(security.get_current_user())])
    async def user_logout():
        return security.get_logout_response()

    if security.settings.USE_REFRESH_TOKEN:

        @router.post("/refresh")
        async def refresh_token(
            service: BaseAuthService = Depends(security.service_dep),
            token: TokenData = Depends(security.get_refresh_token()),
        ):
            tokens = await service.refresh_access_token(token)
            return security.get_login_response(tokens)

    return router
