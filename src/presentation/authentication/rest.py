from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, status

from src.application import authentication, users
from src.domain.users.entities import UserFlat, UserUncommited
from src.infrastructure.application import Response

from .contracts import (
    RefreshAccessTokenRequestBody,
    SignUpRequestBody,
    TokenClaimPublic,
    TokenClaimRequestBody,
    UserPublic,
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

    user = await authentication.authenticate_user(
        schema.username, schema.password
    )
    token_type = authentication.get_token_type()
    access_token_expires = authentication.get_access_token_expiration_time()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={f"WWW-Authenticate": "{token_type}"},
        )

    payload = await authentication.create_payload(user)
    options = {
        "_with": "EMAIL",
        "_from": "PASSWORD",
        "_date": datetime.utcnow().timestamp(),
    }
    access_token = authentication.create_access_token(data=payload, options={})
    refresh_token = authentication.create_refresh_token(
        data={"id": user.id}, options={}
    )
    token_claim = {
        "tokenType": token_type,
        "expiresIn": access_token_expires.total_seconds(),
        "accessToken": access_token,
        "refreshToken": refresh_token,
    }

    return Response[TokenClaimPublic](result=token_claim)


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


@router.post(
    "/signup",
    summary="Create new user",
    response_model=Response[UserPublic],
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    request: Request,
    schema: SignUpRequestBody,
) -> Response[UserPublic]:
    user_exist = await users.get_exist(schema.username)
    if user_exist is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist",
        )

    schema.password = authentication.hash_password(schema.password)
    user: UserFlat = await users.create(UserUncommited(**schema.model_dump()))

    user_public = UserPublic.model_validate(user)
    return Response[UserPublic](result=user_public)
