"""Pydantic request/response models."""

from typing import Literal

from pydantic import BaseModel, Field

from .config import MAX_MIC_SECONDS, MAX_SPEED, MAX_STEPS, MIN_SAFE_DISTANCE_CM


class MoveRequest(BaseModel):
    """A single gait-based locomotion command."""

    action: Literal[
        "forward", "backward", "turn left", "turn right",
        "turn left angle", "turn right angle",
    ] = Field(..., description="Direction of movement.")
    steps: int = Field(
        1, ge=1, le=MAX_STEPS,
        description=f"Number of gait cycles (max {MAX_STEPS}). "
        "Chain requests for longer distances.",
    )
    speed: int = Field(80, ge=1, le=MAX_SPEED, description="Gait speed, 1-100.")
    safety: bool = Field(
        True,
        description=(
            f"If true, 'forward' is refused when ultrasonic reads < {MIN_SAFE_DISTANCE_CM}cm. "
            "Set false only if you've independently verified the path is clear."
        ),
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"action": "forward", "steps": 2, "speed": 80},
                {"action": "turn left angle", "steps": 1, "speed": 70},
            ]
        }
    }


class PoseRequest(BaseModel):
    """Put the robot into a named static pose."""

    pose: Literal["stand", "sit"] = Field(..., description="Target pose.")
    speed: int = Field(80, ge=1, le=MAX_SPEED, description="Transition speed (1-100).")


class SayRequest(BaseModel):
    """Speak text aloud through the on-board speaker."""

    text: str = Field(
        ..., min_length=1, max_length=500, description="Text to speak (max 500 chars).",
    )


class SoundRequest(BaseModel):
    """Play a pre-existing audio file from the Pi's filesystem."""

    path: str = Field(..., description="Absolute path to a .wav or .mp3 file on the Pi.")
    background: bool = Field(False, description="If true, playback is non-blocking.")


class ListenRequest(BaseModel):
    """Record audio from the on-board microphone."""

    duration_seconds: float = Field(
        3.0, gt=0.1, le=MAX_MIC_SECONDS,
        description=f"Recording length in seconds (max {MAX_MIC_SECONDS}).",
    )
    device: str | None = Field(None, description="ALSA device string (e.g. 'plughw:2,0').")


class ActionResult(BaseModel):
    """Standard result envelope for commands."""

    ok: bool = Field(..., description="True if the command was executed, false if refused.")
    detail: str = Field(..., description="Human-readable explanation.")
    elapsed_seconds: float = Field(..., description="Wall-clock duration of the command.")


class DistanceResult(BaseModel):
    """Ultrasonic sensor reading."""

    distance_cm: float = Field(..., description="Distance in centimeters (valid ~2-400cm).")
    timestamp: float = Field(..., description="Unix epoch seconds.")


class SnapshotResult(BaseModel):
    """Camera still image."""

    mime: Literal["image/jpeg"] = Field(...)
    base64: str = Field(..., description="Base64-encoded JPEG bytes.")
    bytes: int = Field(..., description="Decoded byte length.")
    timestamp: float = Field(..., description="Unix epoch seconds.")


class ListenResult(BaseModel):
    """Recorded audio clip."""

    mime: Literal["audio/wav"] = Field(...)
    base64: str = Field(..., description="Base64-encoded WAV bytes.")
    bytes: int = Field(..., description="Decoded byte length.")
    duration_seconds: float = Field(..., description="Actual recorded duration.")


class HealthResult(BaseModel):
    ok: bool
    mock: bool
