"""Hardware abstraction layer.

Provides a Protocol that the route handlers depend on, with real and mock
implementations. The mock lets you develop and test without a Pi.
"""

from __future__ import annotations

import logging
import pathlib
import time
from typing import Protocol

log = logging.getLogger("picrawler")


class Crawler(Protocol):
    def do_action(self, name: str, steps: int, speed: int) -> None: ...
    def do_step(self, name: str, speed: int) -> None: ...
    def get_distance(self) -> float: ...


class Camera(Protocol):
    def start(self) -> None: ...
    def close(self) -> None: ...
    def take_photo(self, name: str, path: str) -> None: ...


class AudioPlayer(Protocol):
    def set_volume(self, volume: int) -> None: ...
    def play(self, path: str) -> None: ...
    def play_background(self, path: str) -> None: ...


class TextToSpeech(Protocol):
    def set_language(self, lang: str) -> None: ...
    def say(self, text: str) -> None: ...


class MockCrawler:
    def do_action(self, name: str, steps: int, speed: int) -> None:
        log.info(f"[mock] do_action({name}, {steps}, {speed})")
        time.sleep(0.05 * steps)

    def do_step(self, name: str, speed: int) -> None:
        log.info(f"[mock] do_step({name}, {speed})")
        time.sleep(0.05)

    def get_distance(self) -> float:
        return 42.0


class MockCamera:
    def start(self) -> None:
        pass

    def close(self) -> None:
        pass

    def take_photo(self, name: str, path: str) -> None:
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        pathlib.Path(f"{path}/{name}.jpg").write_bytes(b"\xff\xd8\xff\xe0mock")


class MockAudioPlayer:
    def set_volume(self, volume: int) -> None:
        pass

    def play(self, path: str) -> None:
        log.info(f"[mock] play({path})")

    def play_background(self, path: str) -> None:
        log.info(f"[mock] play_background({path})")


class MockTTS:
    def set_language(self, lang: str) -> None:
        pass

    def say(self, text: str) -> None:
        log.info(f"[mock] tts.say({text!r})")


class RealCrawler:
    """Wraps picrawler.Picrawler."""

    def __init__(self) -> None:
        from picrawler import Picrawler

        self._hw = Picrawler()

    def do_action(self, name: str, steps: int, speed: int) -> None:
        self._hw.do_action(name, steps, speed)

    def do_step(self, name: str, speed: int) -> None:
        self._hw.do_step(name, speed)

    def get_distance(self) -> float:
        return float(self._hw.get_distance())


class RealCamera:
    """Wraps vilib.Vilib."""

    def start(self) -> None:
        from vilib import Vilib

        Vilib.camera_start(vflip=False, hflip=False)
        # MJPEG stream at http://<pi-ip>:9000/mjpg
        Vilib.display(local=False, web=True)

    def close(self) -> None:
        from vilib import Vilib

        Vilib.camera_close()

    def take_photo(self, name: str, path: str) -> None:
        from vilib import Vilib

        Vilib.take_photo(name, path)


class RealAudioPlayer:
    """Wraps robot_hat.Music."""

    def __init__(self) -> None:
        from robot_hat import Music

        self._hw = Music()

    def set_volume(self, volume: int) -> None:
        self._hw.music_set_volume(volume)

    def play(self, path: str) -> None:
        self._hw.sound_play(path)

    def play_background(self, path: str) -> None:
        self._hw.sound_play_threading(path)


class RealTTS:
    """Wraps robot_hat.TTS."""

    def __init__(self) -> None:
        from robot_hat import TTS

        self._hw = TTS()

    def set_language(self, lang: str) -> None:
        self._hw.lang(lang)

    def say(self, text: str) -> None:
        self._hw.say(text)


def create_hardware(
    mock: bool = False,
) -> tuple[Crawler, Camera, AudioPlayer, TextToSpeech]:
    if mock:
        return MockCrawler(), MockCamera(), MockAudioPlayer(), MockTTS()
    return RealCrawler(), RealCamera(), RealAudioPlayer(), RealTTS()
