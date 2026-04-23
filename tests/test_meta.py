import pytest


@pytest.mark.asyncio
async def test_health_no_auth_required(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["mock"] is True


@pytest.mark.asyncio
async def test_tools_returns_list(client, auth_headers):
    resp = await client.get("/tools", headers=auth_headers)
    assert resp.status_code == 200
    tools = resp.json()["tools"]
    assert len(tools) == 6
    names = {t["function"]["name"] for t in tools}
    assert "picrawler_move" in names
    assert "picrawler_say" in names
