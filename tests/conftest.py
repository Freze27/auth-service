import os
import subprocess
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.database import get_db
from app.main import app

ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:17-alpine") as container:
        yield container


@pytest.fixture(scope="session")
def db_url(postgres_container):
    url = postgres_container.get_connection_url()
    return url.replace("postgresql+psycopg2://", "postgresql+psycopg://")


@pytest.fixture(scope="session", autouse=True)
def apply_migrations(db_url):
    env = {**os.environ, "DATABASE_URL": db_url}
    subprocess.run(["alembic", "upgrade", "head"], env=env, check=True, cwd=ROOT)


@pytest.fixture(scope="session")
def engine(db_url, apply_migrations):
    return create_async_engine(db_url)


@pytest.fixture(autouse=True)
async def clean_tables(engine):
    yield
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE users, user_role RESTART IDENTITY CASCADE"))


@pytest.fixture
async def session(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s


@pytest.fixture
async def client(session):
    async def override():
        yield session

    app.dependency_overrides[get_db] = override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
