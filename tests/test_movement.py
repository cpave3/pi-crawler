
import pytest


@pytest.mark.asyncio
async def test_move_forward(client, auth_headers):
    resp = await client.post("/move", headers=auth_headers, json={
        "action": "forward", "steps": 1, "speed": 80,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert "forward" in data["detail"]


@pytest.mark.asyncio
async def test_move_invalid_steps_returns_422(client, auth_headers):
    resp = await client.post("/move", headers=auth_headers, json={
        "action": "forward", "steps": 99, "speed": 80,
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_move_invalid_action_returns_422(client, auth_headers):
    resp = await client.post("/move", headers=auth_headers, json={
        "action": "fly",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_pose_stand(client, auth_headers):
    resp = await client.post("/pose", headers=auth_headers, json={"pose": "stand"})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


@pytest.mark.asyncio
async def test_pose_sit(client, auth_headers):
    resp = await client.post("/pose", headers=auth_headers, json={"pose": "sit"})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


@pytest.mark.asyncio
async def test_move_forward_safety_refuses_when_close(client, auth_headers):
    from picrawler_server.app import get_state

    state = get_state()
    original = state.crawler.get_distance
    state.crawler.get_distance = lambda: 8.0  # type: ignore[assignment]
    try:
        resp = await client.post("/move", headers=auth_headers, json={
            "action": "forward", "steps": 1, "speed": 80, "safety": True,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is False
        assert "obstacle" in data["detail"]
    finally:
        state.crawler.get_distance = original  # type: ignore[assignment]


@pytest.mark.asyncio
async def test_move_forward_safety_false_overrides(client, auth_headers):
    from picrawler_server.app import get_state

    state = get_state()
    original = state.crawler.get_distance
    state.crawler.get_distance = lambda: 8.0  # type: ignore[assignment]
    try:
        resp = await client.post("/move", headers=auth_headers, json={
            "action": "forward", "steps": 1, "speed": 80, "safety": False,
        })
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
    finally:
        state.crawler.get_distance = original  # type: ignore[assignment]


@pytest.mark.asyncio
async def test_stop(client, auth_headers):
    resp = await client.post("/stop", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["detail"] == "stopped"
