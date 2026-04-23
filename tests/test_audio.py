import pytest


@pytest.mark.asyncio
async def test_say_espeak(client, auth_headers):
    resp = await client.post("/say", headers=auth_headers, json={"text": "hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert "espeak" in data["detail"]


@pytest.mark.asyncio
async def test_say_empty_text_returns_422(client, auth_headers):
    resp = await client.post("/say", headers=auth_headers, json={"text": ""})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_sound_missing_file_returns_404(client, auth_headers):
    resp = await client.post("/sound", headers=auth_headers, json={
        "path": "/nonexistent/file.wav",
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_listen_returns_wav(client, auth_headers):
    resp = await client.post("/listen", headers=auth_headers, json={
        "duration_seconds": 0.5,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["mime"] == "audio/wav"
    assert data["bytes"] > 0


@pytest.mark.asyncio
async def test_listen_duration_too_long_returns_422(client, auth_headers):
    resp = await client.post("/listen", headers=auth_headers, json={
        "duration_seconds": 999,
    })
    assert resp.status_code == 422
