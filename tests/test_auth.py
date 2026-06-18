from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings

REGISTER_PAYLOAD = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123",
    "department_id": 1,
}

LOGIN_PAYLOAD = {
    "username": REGISTER_PAYLOAD["username"],
    "password": REGISTER_PAYLOAD["password"],
}


async def _register_and_login(client) -> dict:
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post("/auth/login", json=LOGIN_PAYLOAD)
    return response.json()


async def test_register_shouldReturn201WithUserData_whenValidPayload(client):
    response = await client.post("/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == REGISTER_PAYLOAD["email"]
    assert data["username"] == REGISTER_PAYLOAD["username"]
    assert "hashed_password" not in data


async def test_register_shouldReturn409_whenEmailAlreadyTaken(client):
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post("/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 409


async def test_login_shouldReturn200WithBothTokens_whenValidCredentials(client):
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post("/auth/login", json=LOGIN_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_login_shouldReturn401_whenWrongPassword(client):
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post("/auth/login", json={
        "username": LOGIN_PAYLOAD["username"],
        "password": "wrongpassword",
    })
    assert response.status_code == 401


async def test_refresh_shouldReturn200WithNewTokenPair_whenValidRefreshToken(client):
    tokens = await _register_and_login(client)
    response = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_refresh_shouldReturn401_whenAccessTokenPassedInstead(client):
    tokens = await _register_and_login(client)
    response = await client.post("/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert response.status_code == 401


async def test_usersMe_shouldReturn200WithUserData_whenValidAccessToken(client):
    tokens = await _register_and_login(client)
    response = await client.get("/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == REGISTER_PAYLOAD["email"]


async def test_usersMe_shouldReturn401_whenNoToken(client):
    response = await client.get("/users/me")
    assert response.status_code == 401


async def test_usersMe_shouldReturn401_whenTokenExpired(client):
    now = datetime.now(timezone.utc)
    expired_token = jwt.encode(
        {
            "sub": "1",
            "type": "access",
            "updated_at": 0,
            "iat": now - timedelta(minutes=30),
            "exp": now - timedelta(minutes=1),
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    response = await client.get("/users/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401


async def test_accessToken_shouldContainRolesAndDepartment_whenUserLogsIn(client):
    tokens = await _register_and_login(client)
    payload = jwt.decode(tokens["access_token"], settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert isinstance(payload["roles"], list)
    assert len(payload["roles"]) > 0
    assert "id" in payload["department"]
    assert "name" in payload["department"]


async def test_accessToken_shouldHaveTtlMatchingConfig_whenUserLogsIn(client):
    tokens = await _register_and_login(client)
    payload = jwt.decode(tokens["access_token"], settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    actual_ttl = payload["exp"] - payload["iat"]
    expected_ttl = settings.ACCESS_TOKEN_TTL_MINUTES * 60
    assert actual_ttl == expected_ttl
