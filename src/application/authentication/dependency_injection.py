from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from src.domain.authentication import (
    AuthenticationRepository,
    TokenOptions,
    TokenPayload,
)
from src.domain.users import UserFlat, UserRepository
from src.infrastructure.application import AuthenticationError
from src.infrastructure.config import settings
from src.infrastructure.database import transaction

__all__ = (
    "authenticate_user",
    "create_payload",
    "create_access_token",
    "create_refresh_token",
    "get_access_token_expiration_time",
    "get_refresh_token_expiration_time",
    "get_token_type",
    "get_current_user",
    "hash_password",
    "verify_password",
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    scheme_name=settings.authentication.scheme,
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(password, hashed_password)
    except:
        return False


async def authenticate_user(username: str, password: str):
    async with transaction():
        user = await AuthenticationRepository().get_user(username=username)
        if not user:
            return False
        if not verify_password(password, user.password):
            return False
        return user


async def create_payload(user: UserFlat) -> dict:
    async with transaction():
        return await AuthenticationRepository().create_payload(user)


def create_access_token(data: dict, options: TokenOptions):
    to_encode = data.copy()
    expire = datetime.utcnow() + get_access_token_expiration_time()
    to_encode.update({"exp": expire}, **options)
    encoded_jwt = jwt.encode(
        to_encode,
        settings.authentication.access_token.secret_key,
        algorithm=settings.authentication.algorithm,
    )
    return encoded_jwt


def create_refresh_token(data: dict, options: TokenOptions):
    to_encode = data.copy()
    expire = datetime.utcnow() + get_refresh_token_expiration_time()
    to_encode.update({"exp": expire}, **options)
    encoded_jwt = jwt.encode(
        to_encode,
        settings.authentication.refresh_token.secret_key,
        algorithm=settings.authentication.algorithm,
    )
    return encoded_jwt


def get_access_token_expiration_time():
    return timedelta(hours=settings.authentication.access_token.ttl)


def get_refresh_token_expiration_time():
    return timedelta(days=settings.authentication.refresh_token.ttl)


def get_token_type():
    return settings.authentication.scheme


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserFlat:
    try:
        payload = jwt.decode(
            token,
            settings.authentication.access_token.secret_key,
            algorithms=[settings.authentication.algorithm],
        )
        print(payload)
        token_payload = TokenPayload(**payload)

        if datetime.fromtimestamp(token_payload.exp) < datetime.now():
            raise AuthenticationError
    except (JWTError, ValidationError) as err:
        print(err)
        raise AuthenticationError from err

    async with transaction():
        user = await UserRepository().get(id=token_payload.sub)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not find user",
            )
    # TODO: Check if the token is in the blacklist

    return user
