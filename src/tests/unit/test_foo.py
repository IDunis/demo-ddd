from src.domain.users import UserRepository
from src.domain.users.tests import factories

# NOTE: Just an example of working of database cleaning up


async def test_user_creation_not_performed():
    users_number = await UserRepository()._count()

    assert users_number == 0


async def test_user_creation():
    # Prepare the test data
    await factories.create_user()

    # Perform some operations
    users_number = await UserRepository()._count()

    assert users_number == 1
