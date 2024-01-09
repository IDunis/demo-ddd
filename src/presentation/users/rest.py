import structlog
from fastapi import APIRouter, Depends, Request, status

from src.application import authentication, users
from src.domain.users import (
    UserFlat,
)
from src.infrastructure.application import Response, ResponseMulti

from .contracts import UserPublic

logger = structlog.stdlib.get_logger()
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", status_code=status.HTTP_200_OK)
async def users_list(request: Request, user: UserFlat = Depends(authentication.get_current_user)) -> ResponseMulti[UserPublic]:
    """Get all users."""

    _users: list[UserFlat] = await users.get_all()
    # await logger.info("test")
    _users_public: list[UserPublic] = [
        UserPublic.model_validate(_user) for _user in _users
    ]

    return ResponseMulti[UserPublic](result=_users_public)
