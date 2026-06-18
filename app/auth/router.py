from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service
from app.auth.schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    response_description="Пользователь успешно зарегистрирован",
    responses={
        409: {"description": "Email или username уже занят"},
        404: {"description": "Подразделение не найдено"},
        422: {"description": "Невалидные данные (короткий пароль, неверный формат email)"},
    },
)
async def register(body: RegisterRequest, session: AsyncSession = Depends(get_db)):
    user = await service.register(
        session,
        email=body.email,
        username=body.username,
        password=body.password,
        department_id=body.department_id,
    )
    return UserResponse.from_orm_user(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    response_description="Успешная аутентификация, возвращена пара токенов",
    responses={
        401: {"description": "Неверные данные пользователя"},
        403: {"description": "Пользователь деактивирован"},
    },
)
async def login(body: LoginRequest, session: AsyncSession = Depends(get_db)):
    return await service.login(session, body.username, body.password)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    response_description="Выдана новая пара токенов",
    responses={
        401: {"description": "Невалидный или просроченный токен / передан access token вместо refresh / пользователь деактивирован"},
    },
)
async def refresh(body: RefreshRequest, session: AsyncSession = Depends(get_db)):
    return await service.refresh_tokens(session, body.refresh_token)
