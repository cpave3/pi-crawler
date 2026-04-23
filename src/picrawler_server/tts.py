"""Piper TTS streaming with aplay playback."""

from __future__ import annotations

import asyncio
import logging

import httpx

from .config import MOCK, PIPER_MODE, PIPER_PREBUFFER_MS, PIPER_URL, PIPER_VOICE

log = logging.getLogger("picrawler")


def parse_wav_header(buf: bytes) -> dict | None:
    """Parse a WAV RIFF header. Returns sample_rate, channels, bits_per_sample,
    data_offset, bytes_per_second — or None if the header isn't complete yet."""
    if len(buf) < 44:
        return None
    if buf[:4] != b"RIFF" or buf[8:12] != b"WAVE":
        return None

    pos = 12
    fmt_info = None
    while pos + 8 <= len(buf):
        chunk_id = buf[pos : pos + 4]
        chunk_size = int.from_bytes(buf[pos + 4 : pos + 8], "little")
        body_start = pos + 8

        if chunk_id == b"fmt ":
            if body_start + 16 > len(buf):
                return None
            channels = int.from_bytes(buf[body_start + 2 : body_start + 4], "little")
            sample_rate = int.from_bytes(buf[body_start + 4 : body_start + 8], "little")
            bits_per_sample = int.from_bytes(buf[body_start + 14 : body_start + 16], "little")
            fmt_info = (channels, sample_rate, bits_per_sample)
        elif chunk_id == b"data":
            if fmt_info is None:
                return None
            channels, sample_rate, bits_per_sample = fmt_info
            return {
                "sample_rate": sample_rate,
                "channels": channels,
                "bits_per_sample": bits_per_sample,
                "data_offset": body_start,
                "bytes_per_second": sample_rate * channels * bits_per_sample // 8,
            }

        pos = body_start + chunk_size
    return None


async def _spawn_aplay() -> asyncio.subprocess.Process:
    if MOCK:
        return await asyncio.create_subprocess_exec(
            "cat",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
    return await asyncio.create_subprocess_exec(
        "aplay", "-q", "-",
        stdin=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )


def _build_request_kwargs(text: str) -> tuple[bool, dict | str]:
    """Build httpx request kwargs for the configured Piper mode.
    Returns (ok, kwargs_or_error)."""
    if PIPER_MODE == "json":
        body: dict = {"text": text}
        if PIPER_VOICE:
            body["voice"] = PIPER_VOICE
        return True, {"json": body}
    elif PIPER_MODE == "form":
        return True, {"data": {"text": text}}
    elif PIPER_MODE == "raw":
        return True, {
            "content": text.encode("utf-8"),
            "headers": {"Content-Type": "text/plain"},
        }
    return False, f"unknown PIPER_MODE={PIPER_MODE}"


async def speak_via_piper(text: str) -> tuple[bool, str]:
    """Stream TTS from Piper HTTP server and play via aplay with prebuffering.
    Returns (success, detail). On failure, caller should fall back to espeak."""
    if not PIPER_URL:
        return False, "PIPER_URL not configured"

    ok, result = _build_request_kwargs(text)
    if not ok:
        return False, result  # type: ignore[return-value]
    req_kwargs: dict = result  # type: ignore[assignment]

    full_buffer_mode = PIPER_PREBUFFER_MS < 0

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", PIPER_URL, **req_kwargs) as resp:
                if resp.status_code != 200:
                    err = (await resp.aread()).decode(errors="replace")[:200]
                    return False, f"piper HTTP {resp.status_code}: {err}"

                prebuf = bytearray()
                header = None
                prebuffer_target_bytes = None
                aplay = None
                total_bytes = 0

                async for chunk in resp.aiter_bytes():
                    if not chunk:
                        continue
                    total_bytes += len(chunk)

                    if aplay is None:
                        prebuf.extend(chunk)
                        if header is None:
                            header = parse_wav_header(bytes(prebuf))
                            if header is not None and not full_buffer_mode:
                                bps = header["bytes_per_second"]
                                prebuffer_target_bytes = (
                                    header["data_offset"] + bps * PIPER_PREBUFFER_MS // 1000
                                )
                        if not full_buffer_mode and prebuffer_target_bytes is not None:
                            if len(prebuf) >= prebuffer_target_bytes:
                                aplay = await _spawn_aplay()
                                aplay.stdin.write(bytes(prebuf))  # type: ignore[union-attr]
                                await aplay.stdin.drain()  # type: ignore[union-attr]
                                prebuf.clear()
                    else:
                        aplay.stdin.write(chunk)  # type: ignore[union-attr]
                        await aplay.stdin.drain()  # type: ignore[union-attr]

                if aplay is None:
                    if not prebuf:
                        return False, "piper returned empty response"
                    aplay = await _spawn_aplay()
                    aplay.stdin.write(bytes(prebuf))  # type: ignore[union-attr]
                    await aplay.stdin.drain()  # type: ignore[union-attr]

                aplay.stdin.close()  # type: ignore[union-attr]
                await aplay.wait()
                if aplay.returncode != 0:
                    stderr = (await aplay.stderr.read()).decode(errors="replace")[:200]  # type: ignore[union-attr]
                    return False, f"aplay exit {aplay.returncode}: {stderr}"

                mode = "full-buffer" if full_buffer_mode else f"prebuf={PIPER_PREBUFFER_MS}ms"
                return True, f"piper {total_bytes}B played ({mode})"

    except httpx.RequestError as e:
        return False, f"piper connection failed: {e}"
    except Exception as e:
        return False, f"piper stream error: {e}"
