"""Sensor endpoints: distance, snapshot."""

from __future__ import annotations

import asyncio
import base64
import os
import tempfile
import time

from fastapi import APIRouter, Depends, HTTPException

from ..auth import require_token
from ..models import DistanceResult, SnapshotResult

router = APIRouter(tags=["sensors"], dependencies=[Depends(require_token)])


@router.get("/sensors/distance", response_model=DistanceResult)
async def distance() -> DistanceResult:
    from ..app import get_state

    state = get_state()
    try:
        cm = float(state.crawler.get_distance())
        return DistanceResult(distance_cm=cm, timestamp=time.time())
    except Exception as e:
        raise HTTPException(500, f"sensor read failed: {e}")


@router.get("/camera/snapshot", response_model=SnapshotResult)
async def snapshot() -> SnapshotResult:
    from ..app import get_state

    state = get_state()
    tmpdir = tempfile.mkdtemp(prefix="picrawler_snap_")
    name = f"snap_{int(time.time() * 1000)}"
    await asyncio.to_thread(state.camera.take_photo, name, tmpdir)
    path = os.path.join(tmpdir, f"{name}.jpg")
    if not os.path.exists(path):
        raise HTTPException(500, "camera failed to produce image")
    with open(path, "rb") as f:
        data = f.read()
    os.remove(path)
    os.rmdir(tmpdir)
    return SnapshotResult(
        mime="image/jpeg",
        base64=base64.b64encode(data).decode(),
        bytes=len(data),
        timestamp=time.time(),
    )
