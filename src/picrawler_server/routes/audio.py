"""Audio endpoints: say, sound, listen."""

from __future__ import annotations

import asyncio
import base64
import logging
import os
import subprocess
import tempfile
import time

from fastapi import APIRouter, Depends, HTTPException

from ..auth import require_token
from ..config import MOCK, PIPER_URL
from ..models import ActionResult, ListenRequest, ListenResult, SayRequest, SoundRequest
from ..tts import speak_via_piper

router = APIRouter(tags=["audio"], dependencies=[Depends(require_token)])
log = logging.getLogger("picrawler")


@router.post("/say", response_model=ActionResult)
async def say(req: SayRequest) -> ActionResult:
    from ..app import get_state

    state = get_state()
    t0 = time.time()

    if PIPER_URL:
        ok, detail = await speak_via_piper(req.text)
        if ok:
            return ActionResult(ok=True, detail=detail, elapsed_seconds=time.time() - t0)
        log.warning(f"piper failed ({detail}), falling back to espeak")

    await asyncio.to_thread(state.tts.say, req.text)
    if PIPER_URL:
        return ActionResult(
            ok=True,
            detail=f"espeak fallback (piper failed: {detail})",  # noqa: F821 — detail set in if block above
            elapsed_seconds=time.time() - t0,
        )
    return ActionResult(
        ok=True,
        detail=f"espeak said {len(req.text)} chars",
        elapsed_seconds=time.time() - t0,
    )


@router.post("/sound", response_model=ActionResult)
async def sound(req: SoundRequest) -> ActionResult:
    from ..app import get_state

    state = get_state()
    t0 = time.time()
    if not os.path.exists(req.path):
        raise HTTPException(404, f"no such file: {req.path}")
    if req.background:
        await asyncio.to_thread(state.audio.play_background, req.path)
    else:
        await asyncio.to_thread(state.audio.play, req.path)
    return ActionResult(ok=True, detail=f"played {req.path}", elapsed_seconds=time.time() - t0)


@router.post("/listen", response_model=ListenResult)
async def listen(req: ListenRequest) -> ListenResult:
    fd, path = tempfile.mkstemp(suffix=".wav", prefix="picrawler_mic_")
    os.close(fd)
    try:
        if MOCK:
            import wave

            with wave.open(path, "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(16000)
                w.writeframes(b"\x00\x00" * int(16000 * req.duration_seconds))
        else:
            cmd = ["arecord", "-q", "-f", "cd", "-t", "wav", "-d", str(int(req.duration_seconds))]
            if req.device:
                cmd += ["-D", req.device]
            cmd.append(path)
            await asyncio.to_thread(
                subprocess.run, cmd, check=True,
                capture_output=True, timeout=req.duration_seconds + 5,
            )

        with open(path, "rb") as f:
            data = f.read()
        return ListenResult(
            mime="audio/wav",
            base64=base64.b64encode(data).decode(),
            bytes=len(data),
            duration_seconds=req.duration_seconds,
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(500, f"arecord failed: {e.stderr.decode(errors='replace')[:500]}")
    finally:
        if os.path.exists(path):
            os.remove(path)
