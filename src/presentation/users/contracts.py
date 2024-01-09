from pydantic import Field

from src.infrastructure.application import PublicEntity


class _UserBase(PublicEntity):
    username: str = Field(description="OpenAPI description")
    password: str = Field(description="OpenAPI description")


class UserCreateRequestBody(_UserBase):
    """User create request body."""


class UserPublic(_UserBase):
    """The internal application representation."""

    id: int
