from typing import AsyncGenerator

from src.infrastructure.database import BaseRepository, ProductsTable

from .entities import ProductFlat, ProductUncommited

__all__ = ("ProductRepository",)


class ProductRepository(BaseRepository[ProductsTable]):
    schema_class = ProductsTable

    async def all(self) -> AsyncGenerator[ProductFlat, None]:
        async for instance in self._all():
            yield ProductFlat.model_validate(instance)

    async def get(self, id_: int) -> ProductFlat:
        instance = await self._get(key="id", value=id_)
        return ProductFlat.model_validate(instance)

    async def create(self, schema: ProductUncommited) -> ProductFlat:
        instance: ProductsTable = await self._save(schema.model_dump())
        return ProductFlat.model_validate(instance)
