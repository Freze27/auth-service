from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service
from app.auth.schemas import UserResponse
from app.database import get_db

router = APIRouter(prefix="/users", tags=["users"])
bearer = HTTPBearer()


@router.get("/me", response_model=UserResponse)
async def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    session: AsyncSession = Depends(get_db),
):
    user = await service.get_current_user(session, credentials.credentials)
    return UserResponse.from_orm_user(user)
