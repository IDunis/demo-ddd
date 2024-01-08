from src.domain.users import UserFlat, UserRepository, UserUncommited
from src.infrastructure.database import transaction


async def get_all() -> list[UserFlat]:
    """Get all products from the database."""

    async with transaction():
        return [product async for product in UserRepository().all()]


async def create(schema: UserUncommited) -> UserFlat:
    """Create a database record for the product."""

    async with transaction():
        return await UserRepository().create(schema)


async def get_exist(username: str) -> UserFlat:
    """Find exist user"""

    async with transaction():
        return await UserRepository().get_via_username(username)
