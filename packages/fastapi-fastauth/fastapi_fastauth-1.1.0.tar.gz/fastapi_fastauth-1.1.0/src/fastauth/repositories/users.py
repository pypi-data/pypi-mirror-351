from .base import IBaseRepository
from fastauth.models import UM
from fastauth.types import ID
from typing import Generic, Any
from abc import abstractmethod, ABC


class IUserRepository(Generic[UM, ID], IBaseRepository[UM, ID], ABC):
    model: type[UM]

    @abstractmethod
    async def get_by_login_fields(
        self, login_fields: list[str], value: Any
    ) -> UM | None:
        raise NotImplementedError
