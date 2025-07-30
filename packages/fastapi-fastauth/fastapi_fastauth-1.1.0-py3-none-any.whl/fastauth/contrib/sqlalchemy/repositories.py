from fastauth.repositories.base import IBaseRepository
from fastauth.repositories.oauths import IOAuthRepository
from fastauth.repositories.users import IUserRepository
from fastauth.models import M, UM, UOAM, OAM
from fastauth.types import ID
from typing import Generic, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_


class SQLAlchemyBaseRepository(Generic[M, ID], IBaseRepository[M, ID]):
    async def get_by_pk(self, pk: ID, **kwargs) -> M | None:
        return await self.session.get(self.model, pk)

    async def get_by_field(self, field: str, value: Any, **kwargs) -> M | None:
        qs = select(self.model).filter_by(**{field: value}).limit(1)
        return await self.session.scalar(qs)

    async def create(self, payload: dict[str, Any], **kwargs) -> M:
        instance = self.model(**payload)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: M, payload: dict[str, Any], **kwargs) -> M:
        for key, val in payload.items():
            setattr(instance, key, val)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: M, **kwargs) -> M:
        await self.session.delete(self.model)
        await self.session.commit()
        return instance

    async def get_many(self, **kwargs) -> list[M]:
        pass

    def __init__(self, session: AsyncSession):
        self.session = session


class SQLAlchemyUserRepository(
    Generic[UM, ID], IUserRepository[UM, ID], SQLAlchemyBaseRepository[UM, ID]
):
    async def get_by_login_fields(
        self, login_fields: list[str], value: Any
    ) -> UM | None:
        qs = (
            select(self.model)
            .where(or_(*[getattr(self.model, f) == value for f in login_fields]))
            .limit(1)
        )
        return await self.session.scalar(qs)


class SQLAlchemyOAuthRepository(
    Generic[OAM, ID, UOAM],
    IOAuthRepository[OAM, ID, UOAM],
    SQLAlchemyBaseRepository[OAM, ID],
):
    async def create_and_add_to_user(self, user: UOAM, payload: dict[str, Any]) -> UOAM:
        self.session.add(user)
        instance = self.model(**payload)
        instance.user_id = user.id
        self.session.add(instance)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_and_add_to_user(
        self, user: UOAM, instance: OAM, payload: dict[str, Any]
    ) -> UOAM:
        for key, val in payload.items():
            setattr(instance, key, val)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_oauth_account(
        self, oauth_name: str, account_id: str
    ) -> UOAM | None:
        qs = (
            select(self.user_model)
            .join(self.model, self.model.user_id == self.user_model.id)
            .where(self.model.oauth_name == oauth_name)
            .where(self.model.account_id == account_id)
        )
        res = await self.session.execute(qs)
        return res.unique().scalar_one_or_none()
