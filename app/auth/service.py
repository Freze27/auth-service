import bcrypt
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.logger import logger
from app.auth.exceptions import (
    DepartmentNotFound,
    EmailTaken,
    InvalidCredentials,
    InvalidToken,
    UserInactive,
    UsernameTaken,
)
from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.config import settings
from app.models import Department, Role, User, user_role


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


async def register(
    session: AsyncSession,
    email: str,
    username: str,
    password: str,
    department_id: int,
) -> User:
    if await session.scalar(select(User).where(User.email == email)):
        raise EmailTaken()

    if await session.scalar(select(User).where(User.username == username)):
        raise UsernameTaken()

    department = await session.get(Department, department_id)
    if not department:
        raise DepartmentNotFound()

    default_role = await session.scalar(select(Role).where(Role.name == "user"))

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        department_id=department_id,
    )
    session.add(user)
    await session.flush()

    await session.execute(insert(user_role).values(user_id=user.id, role_id=default_role.id))
    await session.commit()

    result = await session.execute(
        select(User)
        .where(User.id == user.id)
        .options(selectinload(User.department), selectinload(User.roles))
    )
    return result.scalar_one()


async def login(session: AsyncSession, username: str, password: str) -> dict:
    result = await session.execute(
        select(User)
        .where((User.username == username) | (User.email == username))
        .options(selectinload(User.department), selectinload(User.roles))
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        logger.info("Failed login attempt for '%s'", username)
        raise InvalidCredentials()

    if not user.is_active:
        logger.info("Login attempt for inactive user '%s'", username)
        raise UserInactive()

    logger.info("User '%s' logged in successfully", user.username)
    return {
        "access_token": create_access_token(user),
        "refresh_token": create_refresh_token(user.id, user.updated_at.timestamp()),
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_TTL_MINUTES * 60,
    }


async def refresh_tokens(session: AsyncSession, refresh_token: str) -> dict:
    try:
        payload = decode_token(refresh_token)
    except ValueError as e:
        raise InvalidToken(str(e))

    if payload.get("type") != "refresh":
        raise InvalidToken("Expected refresh token")

    user_id = int(payload["sub"])
    result = await session.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.department), selectinload(User.roles))
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise InvalidToken("User not found or deactivated")

    if user.updated_at.timestamp() != payload.get("updated_at"):
        raise InvalidToken("Token has been invalidated")

    return {
        "access_token": create_access_token(user),
        "refresh_token": create_refresh_token(user.id, user.updated_at.timestamp()),
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_TTL_MINUTES * 60,
    }


async def get_current_user(session: AsyncSession, token: str) -> User:
    try:
        payload = decode_token(token)
    except ValueError as e:
        raise InvalidToken(str(e))

    if payload.get("type") != "access":
        raise InvalidToken("Expected access token")

    user_id = int(payload["sub"])
    result = await session.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.department), selectinload(User.roles))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise InvalidToken("User not found")

    if user.updated_at.timestamp() != payload.get("updated_at"):
        raise InvalidToken("Token has been invalidated")

    return user
