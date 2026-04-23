"""Meta endpoints: health, tools."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..auth import require_token
from ..config import MAX_MIC_SECONDS, MAX_SPEED, MAX_STEPS, MOCK, MOVE_ACTIONS, POSE_ACTIONS
from ..models import HealthResult

router = APIRouter(tags=["meta"])


@router.get("/health", response_model=HealthResult)
async def health() -> HealthResult:
    return HealthResult(ok=True, mock=MOCK)


@router.get("/tools", dependencies=[Depends(require_token)])
async def tool_schema() -> dict:
    return {
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "picrawler_move",
                    "description": "Move the PiCrawler. Blocking and serialized.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": sorted(MOVE_ACTIONS),
                                "description": "Direction of movement.",
                            },
                            "steps": {
                                "type": "integer", "minimum": 1, "maximum": MAX_STEPS,
                                "description": "Number of gait cycles.",
                            },
                            "speed": {
                                "type": "integer", "minimum": 1, "maximum": MAX_SPEED,
                                "default": 80,
                            },
                        },
                        "required": ["action"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "picrawler_pose",
                    "description": "Put the PiCrawler into a stand or sit pose.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pose": {"type": "string", "enum": sorted(POSE_ACTIONS)},
                            "speed": {
                                "type": "integer", "minimum": 1, "maximum": MAX_SPEED,
                                "default": 80,
                            },
                        },
                        "required": ["pose"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "picrawler_distance",
                    "description": "Read the ultrasonic distance sensor. Returns cm.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "picrawler_snapshot",
                    "description": "Capture a still image. Returns base64 JPEG.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "picrawler_say",
                    "description": "Speak text aloud through the robot's speaker.",
                    "parameters": {
                        "type": "object",
                        "properties": {"text": {"type": "string", "maxLength": 500}},
                        "required": ["text"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "picrawler_listen",
                    "description": "Record from the microphone. Returns base64 WAV.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "duration_seconds": {
                                "type": "number", "minimum": 0.5,
                                "maximum": MAX_MIC_SECONDS, "default": 3.0,
                            },
                        },
                    },
                },
            },
        ]
    }
