from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.errors import register_exception_handlers
from app.api.routes import router


app = FastAPI(
    title="Music Capability Library API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

register_exception_handlers(app)
app.include_router(router)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
