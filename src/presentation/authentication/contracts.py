from pydantic import Field

from src.infrastructure.application import PublicEntity


class TokenClaimRequestBody(PublicEntity):
    login: str = Field("OpenAPI documentation")
    password: str = Field("OpenAPI documentation")


class RefreshAccessTokenRequestBody(PublicEntity):
    refresh: str = Field("OpenAPI documentation")


class TokenClaimPublic(PublicEntity):
    access_token: str = Field("OpenAPI documentation")
    refresh_token: str = Field("OpenAPI documentation")
    token_expires: str = Field("OpenAPI documentation")
    token_type: str = Field("OpenAPI documentation")


class UserBase(PublicEntity):
    username: str = Field(description="OpenAPI description")
    password: str = Field(description="OpenAPI documentation")


class SignUpRequestBody(UserBase):
    """User create request body."""


class UserPublic(UserBase):
    """The internal application representation."""

    id: int
