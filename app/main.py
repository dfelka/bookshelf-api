from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.errors import AppError
from app.routers import books, health

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="A production-ready REST API for managing a bookstore inventory.",
    version="0.1.0",
    # Disable the built-in ReDoc route; its default CDN tag (redoc@next) is
    # unpublished (404) and renders blank. A pinned bundle is served below.
    redoc_url=None,
)

# Serve ReDoc from a pinned, stable bundle instead of the broken default.
REDOC_JS_URL = "https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js"


@app.get("/redoc", include_in_schema=False)
def redoc_html() -> HTMLResponse:
    """ReDoc docs page, loaded from a pinned CDN bundle."""
    return get_redoc_html(
        openapi_url=app.openapi_url or "/openapi.json",
        title=f"{app.title} - ReDoc",
        redoc_js_url=REDOC_JS_URL,
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
