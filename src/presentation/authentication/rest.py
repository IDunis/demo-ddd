from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, status

from src.application import authentication
from src.infrastructure.application import Response

from .contracts import (
    RefreshAccessTokenRequestBody,
    TokenClaimPublic,
    TokenClaimRequestBody,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/token",
    response_model=Response[TokenClaimPublic],
    status_code=status.HTTP_201_CREATED,
)
async def token_claim(
    request: Request,
    schema: TokenClaimRequestBody,
) -> Response[TokenClaimPublic]:
    """Claim for access and refresh tokens."""

    user = await authentication.authenticate_user(schema.login, schema.password)
    token_type = authentication.get_token_type()
    access_token_expires = authentication.get_access_token_expiration_time()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={f"WWW-Authenticate": "{token_type}"},
        )

    payload = await authentication.create_payload(user)
    options = {"_with":"EMAIL","_from":"PASSWORD","_date":datetime.utcnow()}
    access_token = authentication.create_access_token(data=payload, options=options)
    refresh_token = authentication.create_refresh_token(data=user.id, options=options)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_expires": access_token_expires,
        "token_type": token_type,
    }


@router.post(
    "/token/refresh",
    response_model=Response[TokenClaimPublic],
    status_code=status.HTTP_201_CREATED,
)
async def token_refresh(
    request: Request,
    schema: RefreshAccessTokenRequestBody,
) -> Response[TokenClaimPublic]:
    """Refresh the access token."""

    # 🔗 https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
    raise NotImplementedError
