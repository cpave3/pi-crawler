import os

MOCK = os.environ.get("PICRAWLER_MOCK") == "1"

MAX_STEPS = 10
MAX_SPEED = 100
MIN_SAFE_DISTANCE_CM = 15.0
MAX_MIC_SECONDS = 30

MOVE_ACTIONS = frozenset({
    "forward", "backward", "turn left", "turn right",
    "turn left angle", "turn right angle",
})
POSE_ACTIONS = frozenset({"stand", "sit"})

PIPER_URL = os.environ.get("PIPER_URL", "").rstrip("/")
PIPER_VOICE = os.environ.get("PIPER_VOICE", "")
PIPER_MODE = os.environ.get("PIPER_MODE", "json")
PIPER_PREBUFFER_MS = int(os.environ.get("PIPER_PREBUFFER_MS", "500"))
