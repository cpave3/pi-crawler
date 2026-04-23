"""FastAPI application factory."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import MOCK
from .hardware import create_hardware
from .state import RobotState

log = logging.getLogger("picrawler")

_state: RobotState | None = None


def get_state() -> RobotState:
    if _state is None:
        raise RuntimeError("server not initialized — lifespan hasn't run")
    return _state


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global _state
    log.info("Starting PiCrawler server...")
    crawler, camera, audio, tts = create_hardware(mock=MOCK)
    audio.set_volume(60)
    tts.set_language("en-US")
    camera.start()
    await asyncio.sleep(1.0)
    crawler.do_step("stand", 80)
    _state = RobotState(crawler, camera, audio, tts)
    log.info("PiCrawler ready.")
    yield
    log.info("Shutting down...")
    try:
        crawler.do_step("sit", 60)
    except Exception:
        pass
    try:
        camera.close()
    except Exception:
        pass
    _state = None


def create_app() -> FastAPI:
    app = FastAPI(
        title="PiCrawler Agent Control",
        version="1.0.0",
        lifespan=lifespan,
    )

    from .routes.audio import router as audio_router
    from .routes.meta import router as meta_router
    from .routes.movement import router as movement_router
    from .routes.sensors import router as sensors_router

    app.include_router(meta_router)
    app.include_router(movement_router)
    app.include_router(sensors_router)
    app.include_router(audio_router)

    return app
