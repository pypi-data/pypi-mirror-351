from abc import abstractmethod, ABC

from .base import IBaseRepository
from fastauth.models import RM
from fastauth.types import ID


class IRoleRepository(IBaseRepository[RM, ID], ABC):
    model: type[RM]

    @abstractmethod
    async def get_roles_by_list(self, roles: list[str]) -> list[RM]:
        raise NotImplementedError
