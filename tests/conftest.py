import os

os.environ["PICRAWLER_MOCK"] = "1"
os.environ["PICRAWLER_TOKEN"] = "test-token"

import pytest
from httpx import ASGITransport, AsyncClient

from picrawler_server.app import create_app


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
async def client():
    app = create_app()
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c
