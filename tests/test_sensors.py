import pytest


@pytest.mark.asyncio
async def test_distance_returns_reading(client, auth_headers):
    resp = await client.get("/sensors/distance", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["distance_cm"] == 42.0
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_snapshot_returns_base64_jpeg(client, auth_headers):
    resp = await client.get("/camera/snapshot", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["mime"] == "image/jpeg"
    assert len(data["base64"]) > 0
    assert data["bytes"] > 0
