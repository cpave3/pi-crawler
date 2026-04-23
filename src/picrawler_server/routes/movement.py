"""Movement endpoints: move, pose, stop."""

from __future__ import annotations

import asyncio
import logging
import time

from fastapi import APIRouter, Depends

from ..auth import require_token
from ..config import MIN_SAFE_DISTANCE_CM
from ..models import ActionResult, MoveRequest, PoseRequest

router = APIRouter(tags=["movement"], dependencies=[Depends(require_token)])
log = logging.getLogger("picrawler")


@router.post("/move", response_model=ActionResult)
async def move(req: MoveRequest) -> ActionResult:
    from ..app import get_state

    state = get_state()
    t0 = time.time()
    async with state.lock:
        if req.safety and req.action == "forward":
            try:
                d = float(state.crawler.get_distance())
                if 0 < d < MIN_SAFE_DISTANCE_CM:
                    return ActionResult(
                        ok=False,
                        detail=(
                            f"refused: obstacle {d:.1f}cm ahead "
                            f"(< {MIN_SAFE_DISTANCE_CM}cm). Pass safety=false to override."
                        ),
                        elapsed_seconds=time.time() - t0,
                    )
            except Exception as e:
                log.warning(f"safety read failed, proceeding: {e}")
        await asyncio.to_thread(state.crawler.do_action, req.action, req.steps, req.speed)
    return ActionResult(
        ok=True,
        detail=f"{req.action} x{req.steps} @{req.speed}",
        elapsed_seconds=time.time() - t0,
    )


@router.post("/pose", response_model=ActionResult)
async def pose(req: PoseRequest) -> ActionResult:
    from ..app import get_state

    state = get_state()
    t0 = time.time()
    async with state.lock:
        await asyncio.to_thread(state.crawler.do_step, req.pose, req.speed)
    return ActionResult(ok=True, detail=f"pose={req.pose}", elapsed_seconds=time.time() - t0)


@router.post("/stop", response_model=ActionResult)
async def stop() -> ActionResult:
    from ..app import get_state

    state = get_state()
    t0 = time.time()
    async with state.lock:
        await asyncio.to_thread(state.crawler.do_step, "stand", 80)
    return ActionResult(ok=True, detail="stopped", elapsed_seconds=time.time() - t0)
