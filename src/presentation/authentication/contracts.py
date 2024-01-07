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
