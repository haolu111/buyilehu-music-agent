from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.services.music_education_review_catalog import (
    build_music_education_review_catalog,
    build_music_education_review_preview,
)


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
FRONTEND_DIST_DIR = BASE_DIR.parent / "frontend" / "review-console" / "dist"
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://127.0.0.1:5176,http://localhost:5176",
    ).split(",")
    if origin.strip()
]

app = FastAPI(title="音乐教育组件总审核台", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount(
    "/runtime-assets",
    StaticFiles(directory=STATIC_DIR / "assets"),
    name="runtime-assets",
)


@app.get("/api/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "music-education-review"})


@app.get("/api/music-education-review/catalog")
async def get_music_education_review_catalog() -> JSONResponse:
    return JSONResponse(build_music_education_review_catalog())


@app.get("/api/music-education-review/previews/{category}/{item_id}")
async def get_music_education_review_preview(category: str, item_id: str) -> JSONResponse:
    try:
        return JSONResponse(build_music_education_review_preview(category, item_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


if FRONTEND_DIST_DIR.exists():
    app.mount(
        "/template-console",
        StaticFiles(directory=FRONTEND_DIST_DIR, html=True),
        name="template-console",
    )


@app.get("/")
async def index() -> RedirectResponse:
    return RedirectResponse("/template-console/music-education-review.html")
