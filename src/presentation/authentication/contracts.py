from pydantic import Field

from src.infrastructure.application import PublicEntity


class TokenClaimRequestBody(PublicEntity):
    username: str = Field("OpenAPI documentation")
    password: str = Field("OpenAPI documentation")


class RefreshAccessTokenRequestBody(PublicEntity):
    refresh: str = Field("OpenAPI documentation")


class TokenClaimPublic(PublicEntity):
    tokenType: str = Field("OpenAPI documentation")
    expiresIn: int = Field("OpenAPI documentation")
    accessToken: str = Field("OpenAPI documentation")
    refreshToken: str = Field("OpenAPI documentation")


class UserBase(PublicEntity):
    username: str = Field(description="OpenAPI documentation")
    password: str = Field(description="OpenAPI documentation")


class SignUpRequestBody(UserBase):
    """User create request body."""


class UserPublic(UserBase):
    """The internal application representation."""

    id: int
