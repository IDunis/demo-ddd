from src.domain.users.entities import UserFlat
from src.infrastructure.database import BaseRepository, UsersTable

from .entities import AccessToken, RefreshToken, TokenPayload

all = ("UserRepository",)


class AuthenticationRepository(BaseRepository[UsersTable]):
    schema_class = UsersTable

    async def get_user(self, username: int) -> UserFlat:
        instance = await self._get_or_fail(key="username", value=username)
        return UserFlat.model_validate(instance)

    async def create_payload(self, instance: UserFlat) -> dict:
        return {"sub": str(instance.id)}
