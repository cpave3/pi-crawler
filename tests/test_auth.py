import pytest


@pytest.mark.asyncio
async def test_no_token_returns_401(client):
    resp = await client.get("/sensors/distance")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_wrong_token_returns_401(client):
    resp = await client.get("/sensors/distance", headers={"Authorization": "Bearer wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_valid_token_passes(client, auth_headers):
    resp = await client.get("/sensors/distance", headers=auth_headers)
    assert resp.status_code == 200
