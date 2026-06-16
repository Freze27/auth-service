from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.auth.exceptions import AuthError
from app.auth.router import router as auth_router
from app.database import AsyncSessionLocal
from app.users.router import router as users_router

app = FastAPI(title="Auth Service")

app.include_router(auth_router)
app.include_router(users_router)


@app.exception_handler(AuthError)
async def auth_error_handler(_request: Request, exc: AuthError) -> JSONResponse:
    return JSONResponse(
        {"error": exc.error, "message": exc.message, "details": exc.details},
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    details = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        details[field] = error["msg"]
    return JSONResponse(
        {"error": "validation_error", "message": "Invalid request data", "details": details},
        status_code=422,
    )


@app.exception_handler(HTTPException)
async def http_error_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        {"error": "http_error", "message": exc.detail, "details": {}},
        status_code=exc.status_code,
    )


@app.exception_handler(Exception)
async def internal_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        {"error": "internal_error", "message": "Internal server error", "details": {}},
        status_code=500,
    )


@app.get("/health")
async def health() -> JSONResponse:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return JSONResponse({"status": "ok"})
    except Exception:
        return JSONResponse({"status": "unavailable", "message": "Database connection failed"}, status_code=503)
