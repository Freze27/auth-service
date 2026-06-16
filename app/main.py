from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.auth.router import router as auth_router
from app.database import AsyncSessionLocal
from app.users.router import router as users_router

app = FastAPI(title="Auth Service")

app.include_router(auth_router)
app.include_router(users_router)


@app.get("/health")
async def health() -> JSONResponse:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return JSONResponse({"status": "ok"})
    except Exception:
        return JSONResponse({"status": "unavailable", "message": "Database connection failed"}, status_code=503)
