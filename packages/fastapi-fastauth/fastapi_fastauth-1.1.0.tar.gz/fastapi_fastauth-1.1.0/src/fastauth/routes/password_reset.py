from fastauth.fastauth import FastAuth
from fastapi import Depends
from fastauth.schemas.auth import ResetPasswordRequest
from fastauth.services import BaseAuthService
from fastauth.utils.router import default_router


def get_reset_password_router(security: FastAuth, **kwargs):
    router = default_router(security.settings.ROUTER_AUTH_PREFIX, ["Auth"], **kwargs)

    @router.post("/forgot-password/{email}", status_code=204)
    async def request_forgot_password(
        email: str, service: BaseAuthService = Depends(security.service_dep)
    ):
        await service.request_forgot_password(email)

    @router.post("/reset-password")
    async def reset_password(
        credentials: ResetPasswordRequest,
        service: BaseAuthService = Depends(security.service_dep),
    ):
        await service.reset_user_password(credentials.token, credentials.new_password)

    return router
