from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.database import AsyncSessionLocal

app = FastAPI(title="Auth Service")


@app.get("/health")
async def health() -> JSONResponse:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return JSONResponse({"status": "ok"})
    except Exception:
        return JSONResponse({"status": "unavailable", "message": "Database connection failed"}, status_code=503)
