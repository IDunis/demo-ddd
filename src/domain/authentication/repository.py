from src.domain.users.entities import UserFlat
from src.infrastructure.database import BaseRepository, UsersTable

from .entities import TokenPayload, AccessToken, RefreshToken

all = ("UsersRepository",)


class AuthenticationRepository(BaseRepository[UsersTable]):
    schema_class = UsersTable

    async def get_user(self, _username: int) -> UserFlat:
        instance = await self._get(key="username", value=_username)
        return UserFlat.model_validate(instance)

    async def create_payload(self, instance: UserFlat) -> dict:
        return {"sub": instance.id}
