from typing import Any, AsyncGenerator, Generic, Type

from sqlalchemy import asc, delete, desc, func, select, update
from sqlalchemy.engine import Result

from src.infrastructure.application import (
    DatabaseError,
    NotFoundError,
    UnprocessableError,
)

from ..tables import ConcreteTable
from .session import Session

__all__ = ("BaseRepository",)


class BaseRepository(Session, Generic[ConcreteTable]):
    """This class implements the base interface for working with database
    and makes it easier to work with type annotations.

    The Session class implements the database interaction layer.
    """

    schema_class: Type[ConcreteTable]

    def __init__(self) -> None:
        super().__init__()

        if not self.schema_class:
            raise UnprocessableError(
                message=(
                    "Can not initiate the class without schema_class attribute"
                )
            )

    async def _update(
        self, key: str, value: Any, payload: dict[str, Any]
    ) -> ConcreteTable:
        """Updates an existed instance of the model in the related table.
        If some data is not exist in the payload then the null value will
        be passed to the schema class."""

        query = (
            update(self.schema_class)
            .where(getattr(self.schema_class, key) == value)
            .values(payload)
            .returning(self.schema_class)
        )
        result: Result = await self.execute(query)
        # await self._session.flush()
        await self._session.commit()

        if not (schema := result.scalar_one_or_none()):
            raise DatabaseError

        return schema

    async def _get(self, key: str, value: Any) -> [ConcreteTable, None]:
        """Return only one result by filters"""

        query = select(self.schema_class).where(
            getattr(self.schema_class, key) == value
        )
        result: Result = await self.execute(query)

        if not (_result := result.scalars().one_or_none()):
            return None

        return _result

    async def _get_or_fail(self, key: str, value: Any) -> ConcreteTable:
        """Return only one result by filters"""

        _result: Result = await self._get(key, value)

        if _result is None:
            raise NotFoundError

        return _result

    async def _get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Any = None,
    ) -> AsyncGenerator[ConcreteTable, None]:
        result: Result = await self.execute(
            select(self.schema_class)
            .offset(skip)
            .limit(limit)
            .order_by(order_by or self.schema_class.id)
        )
        schemas = result.scalars().all()

        for schema in schemas:
            yield schema

    async def _count(self) -> int:
        result: Result = await self.execute(func.count(self.schema_class.id))
        value = result.scalar()

        if not isinstance(value, int):
            raise UnprocessableError(
                message=(
                    "For some reason count function returned not an integer."
                    f"Value: {value}"
                ),
            )

        return value

    async def _first(self, by: str = "id") -> ConcreteTable:
        result: Result = await self.execute(
            select(self.schema_class).order_by(asc(by)).limit(1)
        )

        if not (_result := result.scalar_one_or_none()):
            raise NotFoundError

        return _result

    async def _last(self, by: str = "id") -> ConcreteTable:
        result: Result = await self.execute(
            select(self.schema_class).order_by(desc(by)).limit(1)
        )

        if not (_result := result.scalar_one_or_none()):
            raise NotFoundError

        return _result

    async def _save(self, payload: dict[str, Any]) -> ConcreteTable:
        try:
            schema = self.schema_class(**payload)
            self._session.add(schema)
            # await self._session.flush()
            await self._session.commit()
            await self._session.refresh(schema)
            return schema
        except self._ERRORS as err:
            raise DatabaseError from err

    async def _all(self) -> AsyncGenerator[ConcreteTable, None]:
        result: Result = await self.execute(select(self.schema_class))
        schemas = result.scalars().all()

        for schema in schemas:
            yield schema

    async def _delete(self, id: int) -> None:
        await self.execute(
            delete(self.schema_class).where(self.schema_class.id == id)
        )
        await self._session.flush()
