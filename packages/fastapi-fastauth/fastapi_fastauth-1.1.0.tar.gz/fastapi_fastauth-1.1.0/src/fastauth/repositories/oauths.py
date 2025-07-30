from typing import Any, Generic
from .base import IBaseRepository
from fastauth.models import OAM, UOAM
from fastauth.types import ID
from abc import ABC, abstractmethod


class IOAuthRepository(Generic[OAM, ID, UOAM], IBaseRepository[OAM, ID], ABC):
    model: type[OAM]
    user_model: type[UOAM]

    @abstractmethod
    async def create_and_add_to_user(self, user: UOAM, payload: dict[str, Any]) -> UOAM:
        raise NotImplementedError

    @abstractmethod
    async def update_and_add_to_user(
        self, user: UOAM, instance: OAM, payload: dict[str, Any]
    ) -> UOAM:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_oauth_account(
        self, oauth_name: str, account_id: str
    ) -> UOAM | None:
        raise NotImplementedError
