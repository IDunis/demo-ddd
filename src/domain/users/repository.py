from typing import AsyncGenerator

from src.infrastructure.database import BaseRepository, UsersTable

from .entities import UserFlat, UserUncommited

all = ("UserRepository",)


class UserRepository(BaseRepository[UsersTable]):
    schema_class = UsersTable

    async def all(self) -> AsyncGenerator[UserFlat, None]:
        async for instance in self._all():
            yield UserFlat.model_validate(instance)

    async def get(self, id: int) -> UserFlat:
        instance = await self._get_or_fail(key="id", value=id)
        return UserFlat.model_validate(instance)

    async def get_via_username(self, username: str) -> [UserFlat, None]:
        instance = await self._get(key="username", value=username)
        return instance

    async def create(self, schema: UserUncommited) -> UserFlat:
        instance: UsersTable = await self._save(schema.model_dump())
        return UserFlat.model_validate(instance)
