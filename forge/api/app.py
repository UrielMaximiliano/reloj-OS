"""FastAPI application exposing only local read-only observation routes."""

from fastapi import FastAPI

from .routes import router


app = FastAPI(
    title="JOOG Forge Research API",
    version="0.1.0",
    description="Local read-only BLE observation API. No BLE write endpoint is exposed.",
)
app.include_router(router)
