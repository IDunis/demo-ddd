from src.infrastructure.application import InternalEntity

__all__ = (
    "TokenOptions",
    "TokenPayload",
    "AccessToken",
    "RefreshToken",
)


class TokenOptions(InternalEntity):
    _with: str
    _from: str
    _date: str


class TokenPayload(InternalEntity):
    sub: str
    exp: int


class AccessToken(InternalEntity):
    payload: TokenPayload
    raw: str


class RefreshToken(InternalEntity):
    payload: TokenPayload
    raw: str
