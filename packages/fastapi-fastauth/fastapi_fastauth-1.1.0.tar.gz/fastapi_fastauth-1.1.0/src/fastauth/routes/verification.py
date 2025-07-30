from fastapi import Depends

from fastauth.fastauth import FastAuth
from fastauth.schemas.users import BaseUserRead
from fastauth.services import BaseAuthService
from fastauth.utils.router import default_router


def get_verification_router(
    security: FastAuth, user_read: type[BaseUserRead], **kwargs
):
    router = default_router(security.settings.ROUTER_AUTH_PREFIX, ["Auth"], **kwargs)

    @router.post("/request-verification/{email}", status_code=204)
    async def request_verification(
        email: str,
        service: BaseAuthService = Depends(security.service_dep),
    ):
        await service.request_verification(email)

    @router.post("/verify/{token}", response_model=user_read)
    async def verify_user(
        token: str, service: BaseAuthService = Depends(security.service_dep)
    ):
        await service.user_verification(token)

    return router
