from fastauth.models import M
from fastauth.types import ID
from typing import Generic, Any
from abc import ABC, abstractmethod


class IBaseRepository(Generic[M, ID], ABC):
    model: type[M]

    @abstractmethod
    async def get_by_pk(self, pk: ID, **kwargs) -> M | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_field(self, field: str, value: Any, **kwargs) -> M | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, payload: dict[str, Any], **kwargs) -> M:
        raise NotImplementedError

    @abstractmethod
    async def update(self, instance: M, payload: dict[str, Any], **kwargs) -> M:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, instance: M, **kwargs) -> M:
        raise NotImplementedError

    @abstractmethod
    async def get_many(self, **kwargs) -> list[M]:
        raise NotImplementedError
