"""Auth dependency for FastAPI."""

import os

from fastapi import Header, HTTPException


def require_token(authorization: str | None = Header(None)) -> None:
    expected = os.environ.get("PICRAWLER_TOKEN", "changeme")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "missing bearer token")
    if authorization.removeprefix("Bearer ").strip() != expected:
        raise HTTPException(401, "invalid token")
