from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.errors import AppError
from app.routers import books, health

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="A production-ready REST API for managing a bookstore inventory.",
    version="0.1.0",
)


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


@app.exception_handler(AppError)
async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
    return _error_response(exc.status_code, exc.code, exc.message)


@app.exception_handler(StarletteHTTPException)
async def handle_http_exception(
    _: Request, exc: StarletteHTTPException
) -> JSONResponse:
    code = "NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR"
    return _error_response(exc.status_code, code, str(exc.detail))


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    return _error_response(
        422,
        "UNPROCESSABLE_ENTITY",
        "; ".join(
            f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}"
            for err in exc.errors()
        )
        or "Validation failed",
    )


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    """API metadata and quick links to the docs and health check."""
    return {
        "name": settings.app_name,
        "version": app.version,
        "docs": "/docs",
        "health": "/health",
    }


app.include_router(health.router)
app.include_router(books.router)
