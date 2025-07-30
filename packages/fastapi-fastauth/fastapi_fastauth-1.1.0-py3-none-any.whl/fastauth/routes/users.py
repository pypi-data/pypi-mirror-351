from fastapi import Depends
from fastauth import FastAuth
from fastauth.services import BaseAuthService
from fastauth.schemas.users import BaseUserRead, BaseUserUpdate
from fastauth.utils.router import default_router


def get_users_router(
    security: FastAuth,
    user_read: type[BaseUserRead],
    user_update: type[BaseUserUpdate],
    **kwargs,
):
    router = default_router(security.settings.ROUTER_USERS_PREFIX, ["Users"], **kwargs)

    @router.get("/me", response_model=user_read)
    async def get_current_user(user=Depends(security.get_current_user())):
        return user

    @router.patch("/me", response_model=user_read)
    async def patch_current_user(
        payload: user_update,
        user=Depends(security.get_current_user()),
        service: BaseAuthService = Depends(security.service_dep),
    ):
        return await service.patch_user(user, payload, safe=True)

    return router
