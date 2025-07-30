from fastapi import Depends
from fastauth import FastAuth
from fastauth.schemas.users import BaseUserCreate, BaseUserRead
from fastauth.services import BaseAuthService
from fastauth.utils.router import default_router


def get_signup_router(
    security: FastAuth,
    user_create: type[BaseUserCreate],
    user_read: type[BaseUserRead],
    **kwargs,
):
    router = default_router(security.settings.ROUTER_AUTH_PREFIX, ["Auth"], **kwargs)

    @router.post("/signup", response_model=user_read)
    async def user_signup(
        payload: user_create, service: BaseAuthService = Depends(security.service_dep)
    ):
        return await service.signup(payload)

    return router
