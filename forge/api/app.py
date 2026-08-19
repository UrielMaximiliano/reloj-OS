"""FastAPI application exposing local read-only observation routes and web UI."""

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .routes import router


app = FastAPI(
    title="JOOG Forge Research API",
    version="0.1.0",
    description="Local read-only BLE observation API. No BLE write endpoint is exposed.",
)
app.include_router(router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return one predictable error shape while retaining FastAPI's detail key."""

    message = str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error": {"code": f"http_{exc.status_code}", "message": message},
        },
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "error": {"code": "validation_error", "message": "The request could not be validated."},
        },
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Keep unexpected backend errors safe and machine-readable for the web client."""

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Unexpected server error",
            "error": {"code": "internal_error", "message": "Unexpected server error"},
        },
    )


WEB_DIR = Path(__file__).resolve().parents[2] / "web"
app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
