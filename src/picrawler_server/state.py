"""Shared server state — initialized during lifespan, accessed by route handlers."""

from __future__ import annotations

import asyncio

from .hardware import AudioPlayer, Camera, Crawler, TextToSpeech


class RobotState:
    """Holds hardware references and the movement lock."""

    def __init__(
        self,
        crawler: Crawler,
        camera: Camera,
        audio: AudioPlayer,
        tts: TextToSpeech,
    ) -> None:
        self.crawler = crawler
        self.camera = camera
        self.audio = audio
        self.tts = tts
        self.lock = asyncio.Lock()
