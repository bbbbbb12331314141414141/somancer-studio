"""Sonmancer Studio FastAPI Backend — v0.8.0 (Phase 8: Performance + Polish)."""

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel

from aimusic.config import settings
from aimusic.db import init_db
from aimusic.api import projects, songs, lyrics, genres
from aimusic.api import ai as ai_router
from aimusic.api import export as export_router
from aimusic.api import audio as audio_router
from aimusic.api import mixing as mixing_router
from aimusic.api import advanced_export as adv_export_router
from aimusic.api import system as system_router
from aimusic.api.plugins import router as plugins_router, harmony_router

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    environment: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🎵 Sonmancer Studio v0.8.0 starting up…")
    init_db()
    logger.info("✓ Database initialized")

    # Pre-warm directories
    import os
    for d in [settings.projects_dir, settings.exports_dir, settings.temp_dir,
              settings.soundfont_dir, os.path.join(os.getcwd(), "plugins")]:
        os.makedirs(d, exist_ok=True)
    logger.info("✓ Directories initialized")

    yield
    logger.info("🎵 Sonmancer Studio shutting down…")


app = FastAPI(
    title="Sonmancer Studio API",
    description="Cross-platform AI music production environment",
    version="0.8.0",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "tauri://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_handler(_: Any, exc: SQLAlchemyError) -> JSONResponse:
    logger.error(f"DB error: {exc}")
    return JSONResponse(500, {"error": "database_error", "detail": str(exc)})


@app.exception_handler(Exception)
async def general_handler(_: Any, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled: {exc}")
    return JSONResponse(500, {"error": "internal_error", "detail": str(exc)})


@app.get("/")
async def root() -> dict:
    return {"message": "Sonmancer Studio API", "version": "0.8.0"}


@app.get("/api/v1/health")
async def health() -> HealthResponse:
    return HealthResponse(
        status="healthy", version="0.8.0",
        database="connected", environment=settings.environment,
    )


PREFIX = "/api/v1"
app.include_router(projects.router,             prefix=PREFIX)
app.include_router(songs.router,                prefix=PREFIX)
app.include_router(lyrics.router,               prefix=PREFIX)
app.include_router(genres.router,               prefix=PREFIX)
app.include_router(ai_router.router,            prefix=PREFIX)
app.include_router(export_router.router,        prefix=PREFIX)
app.include_router(audio_router.router,         prefix=PREFIX)
app.include_router(mixing_router.router,        prefix=PREFIX)
app.include_router(plugins_router,              prefix=PREFIX)
app.include_router(harmony_router,              prefix=PREFIX)
app.include_router(adv_export_router.router,    prefix=PREFIX)
app.include_router(system_router.router,        prefix=PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "aimusic.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
