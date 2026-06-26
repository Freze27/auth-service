from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service
from app.auth.exceptions import InvalidToken
from app.auth.schemas import UserResponse
from app.database import get_db

router = APIRouter(prefix="/users", tags=["users"])
bearer = HTTPBearer(auto_error=False)


@router.get(
    "/me",
    response_model=UserResponse,
    response_description="Данные текущего пользователя",
    responses={
        401: {"description": "Токен отсутствует, невалиден, просрочен или передан refresh token вместо access"},
    },
)
async def get_me(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(get_db),
):
    if credentials is None:
        raise InvalidToken("Token is missing")
    user = await service.get_current_user(session, credentials.credentials)
    return UserResponse.from_orm_user(user)
